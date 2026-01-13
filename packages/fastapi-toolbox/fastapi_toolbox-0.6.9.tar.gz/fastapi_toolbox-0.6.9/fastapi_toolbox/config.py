import copy
import sys

from uvicorn import Config

from .logging import get_log_level, logger, setup_logging, add_file_log

LOG_LEVEL = get_log_level()

class UvicornConfig(Config):
    """
    自定义配置类,继承自uvicorn的Config类
    非reload模式下,uvicorn使用spawn启动子进程,需要通过config把logger._core传递到子进程里
    reload模式下,使用fork启动子进程,可以直接继承父进程的logger配置
    """

    def __init__(self, *args, **kwargs):
        """
        初始化方法
        保存logger的core对象,并调用父类初始化

        Args:
            filter_callbacks: 可选的过滤回调函数列表，用于过滤日志记录。
                            每个回调函数接收一个record参数，返回True表示过滤掉该日志。
                            常用于过滤特定模块的日志，如SQLAlchemy的低级别日志。
        """
        # 提取callbacks参数
        self.filter_callbacks = kwargs.pop('filter_callbacks', None)

        self.log_file = kwargs.pop("log_file", None)
        self.log_format = kwargs.pop("_format", None)
        self.rotation_size = kwargs.pop("rotation_size", None)
        self.rotation_time = kwargs.pop("rotation_time", None)
        self.retention = kwargs.pop("retention", None)
        self.compression = kwargs.pop("compression", None)
        if kwargs.get("reload", False):
            self.is_reload = True
            self._core = None  # reload uses fork, can't pass core to child
        else:
            self.is_reload = False
            # 这里core.handlers 里只有文件的handler
            # 1. 字典的浅拷贝
            self._core = copy.copy(logger._core)

        super().__init__(*args, **kwargs)

    def configure_logging(self) -> None:
        """
        配置日志
        重写父类的configure_logging方法
        确保子进程logger使用父进程传递过来的core对象
        设置日志配置
        """
        if self.is_reload:
            # reload mode
            if not logger._core.handlers:
                # parent
                logger.add(sys.stderr, level=LOG_LEVEL)
                setup_logging(filter_callbacks=self.filter_callbacks)
            else:
                # child
                setup_logging(filter_callbacks=self.filter_callbacks)
                # add file log in child process
                add_file_log(
                    self.log_file,
                    _format=self.log_format,
                    rotation_size=self.rotation_size,
                    rotation_time=self.rotation_time,
                    retention=self.retention,
                    compression=self.compression,
                )
            return

        super().configure_logging()
        if logger._core.handlers is not self._core.handlers:
            # 3. 父进程里 不会进入这里
            # 子进程里 会进入这里， 使用父进程传递进来的core对象
            logger._core= self._core

            logger.add(sys.stderr, level=LOG_LEVEL)

            setup_logging(filter_callbacks=self.filter_callbacks)
        else:
            # 2. 添加一个handler后
            # 这里loguru logger._core.handlers 会浅拷贝，生成一个新的对象
            # self._core.handlers 还是引用的原有的对像
            # 而原有的对象里只有文件的handler, 这样才能传递到子进程里 (可序列化)
            logger.add(sys.stderr, level=LOG_LEVEL)

            setup_logging(filter_callbacks=self.filter_callbacks)
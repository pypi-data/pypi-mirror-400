# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 使用语言

使用中文

## Project Overview

This is a Python library (`fastapi-toolbox`) that provides common utilities for working with FastAPI applications. The project is in early development stage with minimal structure currently in place.

## Development Environment

- **Package Manager**: uv (modern Python package and project manager)
- **Dependencies**: FastAPI and Starlette for web framework functionality

## Project Structure

- `__init__.py`: Package initialization, exports StaticFilesCache
- `static_files.py`: Static files utilities including StaticFilesCache class
- `main.py`: Entry point with basic hello world functionality
- `pyproject.toml`: Project configuration and metadata

## 核心架构说明

### 多进程日志传递机制 (UvicornConfig)

uvicorn 在多进程模式下使用 `spawn` 方式创建子进程，这会导致 loguru 的 logger 对象无法直接传递（因为 `sys.stderr` 等 IO 对象无法序列化）。

**解决方案设计** (`fastapi_toolbox/config.py`):

1. **父进程初始化时** (`__init__`):
   - 先 `logger.remove()` 移除默认的 stderr handler
   - 只添加文件 handler（可序列化）
   - 浅拷贝 `logger._core` 保存到 `self._core`

2. **浅拷贝的关键作用**:
   ```python
   self._core = copy.copy(logger._core)  # 字典的浅拷贝
   ```
   - 此时 `self._core.handlers` 和 `logger._core.handlers` 指向同一个字典对象
   - 后续父进程添加 stderr handler 时，`logger._core.handlers` 会被浅拷贝成新字典
   - 但 `self._core.handlers` 仍指向原来只有文件 handler 的字典（可序列化）

3. **子进程中的 configure_logging**:
   - 通过比较 `logger._core.handlers is not self._core.handlers` 判断是否在子进程
   - 子进程中：用父进程传递的 `self._core` 替换 `logger._core`，然后重新添加 stderr handler
   - 父进程中：直接添加 stderr handler

4. **运行模式** (`fastapi_toolbox/server.py`):
   - `workers < 2`: 单进程模式，直接 `server.run()`
   - `workers >= 2`: 多进程模式，使用 `Multiprocess` + `spawn`
   - `reload=True`: 热重载模式，使用 `ChangeReload` + `fork`

**reload 模式的特殊处理**:
- fork 模式下子进程继承父进程的内存，不需要传递 logger
- 但文件日志需要在子进程中单独添加，避免多进程写同一文件的问题

## Publishing to PyPI

bash publish.sh

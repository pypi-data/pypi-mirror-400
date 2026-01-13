# Release Notes

## v0.6.8

### 改进

- **日志格式优化**: 更新 `run_server` 函数的日志格式，增加毫秒精度和额外的上下文信息
- **日志配置增强**: 在 `UvicornConfig` 中添加日志配置选项，支持 reload 模式下的文件日志处理
- **热重载重构**: 重构 `server.py` 使用 `ChangeReload` 处理服务器重载，提升代码变更时的服务器响应性能

### 文件变更

- `fastapi_toolbox/config.py`: 新增日志配置选项
- `fastapi_toolbox/server.py`: 日志格式更新、文件日志处理、ChangeReload 重构

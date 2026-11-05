# Open RV Windows 构建

从官方 `AcademySoftwareFoundation/OpenRV` 的 `v4.0.2` 提交
`27db5464a90ca19a9a30d540988ee109ee06bb7e` 构建 Windows x64 便携版。

沿用官方 Windows composite action 的步骤，调整工作目录、Python 路径和构建选项，
显式启用 ProRes、AAC 解码。完成后检查产物中 ProRes、AAC、H.264 解码器是否存在。
流程只支持手动触发，无定时任务，不上传用户视频，不修改本机安装。

源码固定在云端 runner 的 `D:\rv`，遵循官方 Windows 文档的短路径建议，
避免 PySide 生成的目标文件路径超过 Windows 工具链限制。
构建配置、依赖、主程序的日志分别保存；依赖中间目录通过 Actions cache 保留，
仅在源码、工具链与解码器配置兼容时复用。

在 Actions 中手动运行 `Build Open RV Windows with ProRes`，成功产物保留 7 天。
解码器检查通过不代表实际播放验收通过，下载后仍须测试目标素材。

Open RV 及其依赖的许可证、第三方声明以官方源码和产物附带文件为准。
ProRes 配置要求见官方 `docs/build_system/config_common_build.md`。

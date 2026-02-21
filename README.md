# YourApp License Pack (v3)

核心：离线批量授权（一次签名，多台设备）

- 客户侧：生成 REQ-*.json（每台电脑一个）
- 你侧：目录扫描 REQ 文件 → 提取 machine_id → 生成一份多机白名单 license.lic（device_ids）

仍包含：
- lic-v1: JSON + Ed25519 签名
- max_concurrency 同机并发（可选）
- PySide6 授权失败弹窗 & About 页面模板

依赖：
pip install pynacl platformdirs

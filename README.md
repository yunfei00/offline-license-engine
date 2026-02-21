# YourApp License System (v4)
快速环境配置与使用指南
更新时间：2026-02-21

---

# 一、系统要求

- Windows 10 / Windows 11
- Python 3.9 – 3.11
- 推荐使用虚拟环境（venv）

---

# 二、快速安装步骤（开发环境）

## 1️⃣ 创建虚拟环境

```bash
python -m venv venv
venv\Scripts\activate
```

## 2️⃣ 安装依赖

```bash
pip install pynacl platformdirs pyinstaller pyside6 reportlab python-docx
```

---

# 三、生成密钥（只需执行一次）

```bash
python tools/gen_keys.py
```

保存输出：

- PRIVATE_KEY_B64（妥善保管，仅签发端使用）
- PUBLIC_KEY_B64（填入 app/licensing.py 中）

修改：

```python
PUBLIC_KEY_B64 = "你的公钥"
```

---

# 四、客户侧流程

## 1️⃣ 打包设备请求工具

```bash
pyinstaller -F -n YourApp-DeviceRequest tools/make_device_request.py
```

## 2️⃣ 客户运行

会生成：

```
REQ-YYYYMMDD-XXXX.json
```

客户将文件发给你。

---

# 五、批量签发 License（一次签名多设备）

将所有 REQ 文件放入同一目录，例如：

```
requests/张三_20260221/
```

执行：

```bash
python tools/batch_issue_from_requests.py \
  --private_key_b64 "<PRIVATE_KEY>" \
  --requests_dir "requests/张三_20260221" \
  --expires_at "2026-12-31" \
  --grace_days 3 \
  --out license.lic
```

生成：

- license.lic
- license.report.json

将 license.lic 发给客户。

---

# 六、客户端集成校验

在程序入口加入：

```python
from app.licensing import ensure_licensed, LicenseError

try:
    lic = ensure_licensed()
except LicenseError as e:
    print("授权失败：", e)
    exit(1)
```

---

# 七、时间限制机制说明

- expires_at 到期后进入 grace_days 宽限期
- 超过宽限期将拒绝运行
- 若检测到系统时间回退，将提示重新激活

---

# 八、打包主程序

```bash
pyinstaller -F main.py
```

确保：

- license.lic 与 exe 同目录
- 或设置环境变量 YOURAPP_LICENSE_PATH

---

# 九、常见问题

❓ 授权失败怎么办？
→ 检查 license 是否匹配机器

❓ 修改系统时间能否绕过？
→ 不可。系统会检测时间回退

❓ 更换电脑怎么办？
→ 重新生成设备请求文件并重新签发

---

# 十、目录结构说明

```
app/
  licensing.py
  machine_id.py
  time_guard.py
tools/
  gen_keys.py
  make_device_request.py
  batch_issue_from_requests.py
main.py
```
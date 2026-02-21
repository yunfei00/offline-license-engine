# 离线批量授权（一次签名，多台设备）— Windows

## 目标
- 客户每台电脑生成一个 **设备请求文件**（文件名都不同）
- 客户把这些文件发你（zip/列表均可）
- 你把文件放入一个目录，运行一次脚本，生成 **一份** `license.lic`
- 该 license 同时允许多台设备运行（`device_ids` 白名单）

---

## 一、客户侧：生成设备请求文件（每台电脑一个）

### 方式 1：打包成 exe（推荐）
```bash
pyinstaller -F -n YourApp-DeviceRequest tools/make_device_request.py
```

客户运行 `YourApp-DeviceRequest.exe` 后，会在当前目录生成：
- `REQ-YYYYMMDD-XXXXXXXX.json`

把所有 REQ 文件打包发送给你即可。

---

## 二、你侧：批量签发一份 license（一次签名）

1) 解压客户文件到一个目录，例如：
```
requests/张三_20260205/
  REQ-....json
  REQ-....json
```

2) 运行批量签发：
```bash
python tools/batch_issue_from_requests.py \
  --private_key_b64 "<PRIVATE_KEY_B64>" \
  --requests_dir "requests/张三_20260205" \
  --customer "张三" \
  --max_concurrency 1 \
  --out license.lic
```

- 不传 `--customer`：默认取目录名作为 customer
- 会生成 `license.report.json`：用于留档（包含坏文件列表、seat_count 等）

3) 把生成的 `license.lic` 发给客户。

---

## 三、客户侧：使用 license
把 `license.lic` 放到软件同目录（与 exe 同目录）即可。

---

更新时间：2026-02-05

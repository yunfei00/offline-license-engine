from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTextEdit

def _mask_machine_id(mid: str) -> str:
    if not mid:
        return ""
    return f"{mid[:8]}...{mid[-6:]}"

class AboutDialog(QDialog):
    def __init__(self, app_name: str, version: str, lic_info: dict | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"关于 {app_name}")
        self.setMinimumWidth(520)

        lic_info = lic_info or {}
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"<h2>{app_name}</h2>"))
        layout.addWidget(QLabel(f"版本：{version}"))

        layout.addWidget(QLabel("<h3>授权信息</h3>"))
        layout.addWidget(QLabel(f"授权对象：{lic_info.get('customer','未授权')}"))
        lid = lic_info.get("license_id","")
        if lid:
            layout.addWidget(QLabel(f"License ID：{lid}"))

        layout.addWidget(QLabel(f"授权类型：{lic_info.get('type','-') or '-'}"))
        layout.addWidget(QLabel(f"本机标识：{_mask_machine_id(lic_info.get('machine_id','')) or '-'}"))

        sc = lic_info.get("seat_count", None)
        if sc is not None:
            layout.addWidget(QLabel(f"授权设备数：{sc}"))

        feats = lic_info.get("features", [])
        layout.addWidget(QLabel(f"功能模块：{', '.join(feats) if feats else '-'}"))

        mc = lic_info.get("max_concurrency", None)
        layout.addWidget(QLabel(f"同机最大并发：{mc if mc is not None else '-'}"))

        lic_path = lic_info.get("license_path", "")
        if lic_path:
            layout.addWidget(QLabel("License 路径："))
            te = QTextEdit()
            te.setReadOnly(True)
            te.setText(lic_path)
            te.setFixedHeight(60)
            layout.addWidget(te)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn = QPushButton("关闭")
        btn.clicked.connect(self.accept)
        btn_row.addWidget(btn)
        layout.addLayout(btn_row)

# -*- coding: utf-8 -*-
"""
主应用程序窗口
==============

USB-USART 键盘转发器 & 串口调试助手的 Tkinter 界面与事件处理。
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from usart_keyboard.constants import (
    BAUD_PRESETS,
    DATA_BITS_OPTS,
    PARITY_OPTS,
    SKIP_KEYS,
    STOP_BITS_OPTS,
)
from usart_keyboard.serial_manager import (
    SerialManager,
    build_params,
    enumerate_ports,
    parse_port_name,
)


class USARTKeyboardApp:
    """USB-USART 键盘转发器 / 串口调试助手 主窗口。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("USB-USART 键盘转发器 & 串口调试助手")
        self.root.geometry("820x620")
        self.root.minsize(640, 480)

        # 串口管理器
        self.serial_mgr = SerialManager()

        # 构建界面
        self._build_ui()
        self.refresh_ports()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ════════════════════════════════════════════════════════
    # 界面构建
    # ════════════════════════════════════════════════════════

    def _build_ui(self) -> None:
        """构建完整的四行用户界面。"""
        self._build_config_bar()
        self._build_control_bar()
        self._build_send_panel()
        self._build_rx_panel()

        ttk.Label(
            self.root,
            text="提示：发送区内每个按键立即转发；接收区实时显示设备回传数据",
            foreground="gray",
            font=("", 9),
        ).pack(pady=(0, 4))

    # ── 第一行：串口参数配置 ────────────────────────────

    def _build_config_bar(self) -> None:
        cfg = ttk.Frame(self.root, padding=6)
        cfg.pack(fill=tk.X)

        ttk.Label(cfg, text="COM:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar()
        self.port_cb = ttk.Combobox(
            cfg, textvariable=self.port_var, width=22, state="readonly",
        )
        self.port_cb.pack(side=tk.LEFT, padx=3)

        ttk.Label(cfg, text="  波特率:").pack(side=tk.LEFT)
        self.baud_var = tk.StringVar(value="115200")
        self.baud_cb = ttk.Combobox(
            cfg, textvariable=self.baud_var, values=BAUD_PRESETS,
            width=9, state="readonly",
        )
        self.baud_cb.pack(side=tk.LEFT, padx=3)

        ttk.Label(cfg, text="  数据位:").pack(side=tk.LEFT)
        self.data_var = tk.StringVar(value="8")
        self.data_cb = ttk.Combobox(
            cfg, textvariable=self.data_var,
            values=[o[0] for o in DATA_BITS_OPTS], width=4, state="readonly",
        )
        self.data_cb.pack(side=tk.LEFT, padx=3)

        ttk.Label(cfg, text="  校验:").pack(side=tk.LEFT)
        self.parity_var = tk.StringVar(value="None")
        self.parity_cb = ttk.Combobox(
            cfg, textvariable=self.parity_var,
            values=[o[0] for o in PARITY_OPTS], width=6, state="readonly",
        )
        self.parity_cb.pack(side=tk.LEFT, padx=3)

        ttk.Label(cfg, text="  停止位:").pack(side=tk.LEFT)
        self.stop_var = tk.StringVar(value="1")
        self.stop_cb = ttk.Combobox(
            cfg, textvariable=self.stop_var,
            values=[o[0] for o in STOP_BITS_OPTS], width=4, state="readonly",
        )
        self.stop_cb.pack(side=tk.LEFT, padx=3)

    # ── 第二行：操作按钮 + 状态 ─────────────────────────

    def _build_control_bar(self) -> None:
        ctrl = ttk.Frame(self.root, padding=(6, 0, 6, 4))
        ctrl.pack(fill=tk.X)

        ttk.Button(ctrl, text="🔄 刷新", command=self.refresh_ports).pack(
            side=tk.LEFT, padx=2,
        )

        self.toggle_btn = ttk.Button(
            ctrl, text="打开连接", command=self.toggle_connection,
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=4)

        self.status_var = tk.StringVar(value="● 未连接")
        self.status_lbl = ttk.Label(
            ctrl, textvariable=self.status_var,
            foreground="red", font=("", 10, "bold"),
        )
        self.status_lbl.pack(side=tk.LEFT, padx=12)

        self.rx_count_var = tk.StringVar(value="RX: 0 字节")
        ttk.Label(ctrl, textvariable=self.rx_count_var,
                  foreground="gray").pack(side=tk.RIGHT, padx=6)

    # ── 第三行：发送区 ─────────────────────────────────

    def _build_send_panel(self) -> None:
        send_frame = ttk.LabelFrame(self.root, text="发送区", padding=4)
        send_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(4, 0))

        self.send_text = tk.Text(
            send_frame, wrap=tk.WORD, font=("Consolas", 12),
            height=6, relief=tk.SUNKEN, borderwidth=2,
        )
        self.send_text.pack(fill=tk.BOTH, expand=True)
        self.send_text.bind("<KeyPress>", self._on_key_press)
        self.send_text.bind("<KeyRelease>", self._on_key_release)

        send_opts = ttk.Frame(send_frame)
        send_opts.pack(fill=tk.X, pady=(4, 0))

        self.hex_send_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(send_opts, text="HEX 发送",
                        variable=self.hex_send_var).pack(side=tk.LEFT)

        ttk.Label(send_opts, text="  |  输入 HEX 字节（空格分隔）:"
                  ).pack(side=tk.LEFT, padx=(10, 4))
        self.hex_entry = tk.Entry(send_opts, width=30)
        self.hex_entry.pack(side=tk.LEFT)
        self.hex_entry.bind("<Return>", self._send_hex_entry)
        ttk.Button(send_opts, text="发送 HEX",
                   command=self._send_hex_entry).pack(side=tk.LEFT, padx=4)

        ttk.Label(send_opts, text="  (发送区直接打字即转发) ",
                  foreground="gray", font=("", 9)).pack(side=tk.RIGHT)

    # ── 第四行：接收区 ─────────────────────────────────

    def _build_rx_panel(self) -> None:
        rx_frame = ttk.LabelFrame(self.root, text="接收区", padding=4)
        rx_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(4, 6))

        rx_opts = ttk.Frame(rx_frame)
        rx_opts.pack(fill=tk.X)

        self.hex_rx_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(rx_opts, text="HEX 显示",
                        variable=self.hex_rx_var,
                        command=self._toggle_rx_display).pack(side=tk.LEFT)

        self.pause_rx_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(rx_opts, text="暂停滚动",
                        variable=self.pause_rx_var).pack(side=tk.LEFT, padx=10)

        ttk.Button(rx_opts, text="清空接收",
                   command=self._clear_rx).pack(side=tk.RIGHT)

        self.rx_text = tk.Text(
            rx_frame, wrap=tk.WORD, font=("Consolas", 11),
            height=10, relief=tk.SUNKEN, borderwidth=2,
        )
        self.rx_text.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self.rx_text.bind("<KeyPress>", lambda _e: "break")

    # ════════════════════════════════════════════════════════
    # 串口枚举
    # ════════════════════════════════════════════════════════

    def refresh_ports(self) -> None:
        """刷新可用串口列表。"""
        items = enumerate_ports()
        self.port_cb["values"] = items
        if items:
            self.port_cb.current(0)
        else:
            self.port_var.set("")

    # ════════════════════════════════════════════════════════
    # 连接管理
    # ════════════════════════════════════════════════════════

    def toggle_connection(self) -> None:
        if self.serial_mgr.is_open:
            self._close_serial()
        else:
            self._open_serial()

    def _open_serial(self) -> None:
        raw = self.port_var.get()
        if not raw:
            messagebox.showwarning("提示", "请先选择一个 COM 端口")
            return

        port = parse_port_name(raw)
        try:
            baud = int(self.baud_var.get())
        except ValueError:
            messagebox.showwarning("提示", "波特率格式不正确")
            return

        params = build_params(
            port, baud,
            self.data_var.get(),
            self.parity_var.get(),
            self.stop_var.get(),
        )
        err = self.serial_mgr.open(params)
        if err is not None:
            messagebox.showerror("连接失败", f"无法打开串口:\n{err}")
            return

        # 更新 UI 状态
        self._set_ui_connected(True)
        self._set_config_widgets_state(tk.DISABLED)
        self.toggle_btn.config(text="关闭连接")
        self.status_var.set(f"● 已连接 — {params['port']} @ {params['baudrate']}")
        self.status_lbl.config(foreground="green")
        self.send_text.focus_set()

        # 启动接收线程（回调通过 root.after 切换到主线程）
        self.serial_mgr.start_receiving(
            on_data=lambda d: self.root.after(0, self._append_rx_data, d),
            on_count=lambda c: self.root.after(0, self._update_rx_count, c),
            on_disconnect=lambda: self.root.after(0, self._close_serial),
        )

    def _close_serial(self) -> None:
        self.serial_mgr.close()
        self._set_ui_connected(False)
        self._set_config_widgets_state(tk.NORMAL)
        self.toggle_btn.config(text="打开连接")
        self.status_var.set("● 未连接")
        self.status_lbl.config(foreground="red")

    def _set_config_widgets_state(self, state: str) -> None:
        for cb in (self.port_cb, self.baud_cb, self.data_cb,
                   self.parity_cb, self.stop_cb):
            cb.config(state=state)

    def _set_ui_connected(self, connected: bool) -> None:
        if connected:
            self.send_text.config(foreground="black", background="white")
        else:
            self.send_text.config(foreground="gray", background="#f5f5f5")

    # ════════════════════════════════════════════════════════
    # 接收数据处理
    # ════════════════════════════════════════════════════════

    def _append_rx_data(self, data: bytes) -> None:
        """追加接收数据到显示区（主线程调用）。"""
        if self.hex_rx_var.get():
            hex_str = " ".join(f"{b:02X}" for b in data) + " "
            self.rx_text.insert(tk.END, hex_str)
        else:
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = ""
                for b in data:
                    try:
                        text += bytes([b]).decode("utf-8")
                    except UnicodeDecodeError:
                        text += f"\\x{b:02X}"
            self.rx_text.insert(tk.END, text)

        if not self.pause_rx_var.get():
            self.rx_text.see(tk.END)

    def _update_rx_count(self, count: int) -> None:
        self.rx_count_var.set(f"RX: {count} 字节")

    def _toggle_rx_display(self) -> None:
        """HEX / ASCII 显示切换。切换后只影响新数据，已显示内容不变。"""
        pass

    def _clear_rx(self) -> None:
        self.rx_text.delete("1.0", tk.END)
        self.rx_count_var.set("RX: 0 字节")

    # ════════════════════════════════════════════════════════
    # 键盘事件（即按即发）
    # ════════════════════════════════════════════════════════

    def _on_key_press(self, event: tk.Event) -> None:
        """按键按下 → 字符立即转发到串口。"""
        if not self.serial_mgr.is_open:
            return

        ks = event.keysym
        # 特殊功能键
        KEY_MAP = {
            "Return":   b"\r\n",
            "Tab":      b"\t",
            "Escape":   b"\x1b",
            "BackSpace": b"\x08",
        }
        if ks in KEY_MAP:
            self.serial_mgr.write(KEY_MAP[ks])
            return

        # 跳过修饰 / 导航 / 功能键
        if ks in SKIP_KEYS or not event.char:
            return

        self.serial_mgr.write(event.char.encode("utf-8"))

    @staticmethod
    def _on_key_release(_event: tk.Event) -> None:
        """键释放事件（目前不需要特殊处理）。"""
        pass

    # ════════════════════════════════════════════════════════
    # HEX 发送入口
    # ════════════════════════════════════════════════════════

    def _send_hex_entry(self, event: tk.Event | None = None) -> None:
        """从 HEX 输入框读取十六进制字符串并发送。"""
        if not self.serial_mgr.is_open:
            messagebox.showwarning("提示", "请先打开串口连接")
            return

        hex_str = self.hex_entry.get().strip()
        if not hex_str:
            return

        hex_clean = hex_str.replace(" ", "").replace("\t", "").replace("\n", "")
        if not hex_clean:
            return
        if len(hex_clean) % 2 != 0:
            messagebox.showwarning(
                "HEX 格式错误",
                "HEX 字符串长度必须为偶数（每两个字符表示一个字节）\n"
                "正确示例: 41 42 43 或 414243",
            )
            return

        try:
            data = bytes.fromhex(hex_clean)
        except ValueError as exc:
            messagebox.showwarning("HEX 格式错误", f"无法解析 HEX 字符串:\n{exc}")
            return

        self.serial_mgr.write(data)
        self.hex_entry.focus_set()

    # ════════════════════════════════════════════════════════
    # 窗口生命周期
    # ════════════════════════════════════════════════════════

    def _on_close(self) -> None:
        self.serial_mgr.close()
        self.root.destroy()

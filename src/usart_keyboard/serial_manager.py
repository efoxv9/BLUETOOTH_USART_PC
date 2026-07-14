# -*- coding: utf-8 -*-
"""
串口管理器
==========

端口枚举、连接生命周期管理、数据收发。
完全 Tkinter 无关，通过回调与 UI 层解耦。
"""

import threading
import time
from collections.abc import Callable

import serial
import serial.tools.list_ports

from usart_keyboard.constants import DATA_BITS_OPTS, PARITY_OPTS, STOP_BITS_OPTS


# ── 工具函数 ──────────────────────────────────────────────

def enumerate_ports() -> list[str]:
    """枚举系统可用串口，返回 ``"COM3 — 描述"`` 格式的列表。"""
    return [f"{p.device} — {p.description}" for p in serial.tools.list_ports.comports()]


def parse_port_name(raw: str) -> str:
    """从 ``"COM3 — 描述"`` 中提取纯设备名 ``COM3``。"""
    for sep in (" — ", " - "):
        if sep in raw:
            return raw.split(sep)[0]
    return raw


def _lookup(opts: list[tuple[str, int]], label: str, default: int) -> int:
    for k, v in opts:
        if k == label:
            return v
    return default


def build_params(
    port: str,
    baud: int,
    data_bits_label: str,
    parity_label: str,
    stop_bits_label: str,
) -> dict:
    """将界面下拉框的标签值转换为 PySerial 参数字典。"""
    return {
        "port":     port,
        "baudrate": baud,
        "bytesize": _lookup(DATA_BITS_OPTS, data_bits_label, serial.EIGHTBITS),
        "parity":   _lookup(PARITY_OPTS,    parity_label,    serial.PARITY_NONE),
        "stopbits": _lookup(STOP_BITS_OPTS, stop_bits_label, serial.STOPBITS_ONE),
        "timeout":  0.05,      # 接收超时 50 ms，保证界面响应
    }


# ── 连接管理器 ────────────────────────────────────────────

class SerialManager:
    """串口连接生命周期管理（线程安全的 打开/关闭/读写）。"""

    def __init__(self) -> None:
        self.serial_port: serial.Serial | None = None
        self._is_open = False
        self._rx_active = False
        self._rx_thread: threading.Thread | None = None

    # ── 属性 ────────────────────────────────────────────

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def port_name(self) -> str:
        return self.serial_port.port if self.serial_port else "???"

    @property
    def baudrate(self) -> int:
        return self.serial_port.baudrate if self.serial_port else 0

    # ── 打开 / 关闭 ────────────────────────────────────

    def open(self, params: dict) -> str | None:
        """打开串口。成功返回 ``None``，失败返回错误消息。"""
        try:
            self.serial_port = serial.Serial(**params)
        except Exception as exc:
            return str(exc)
        self._is_open = True
        return None

    def close(self) -> None:
        """停止接收线程并关闭串口。"""
        self._rx_active = False
        if self._rx_thread is not None:
            self._rx_thread.join(timeout=1)
            self._rx_thread = None
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
            except Exception:
                pass
        self.serial_port = None
        self._is_open = False

    # ── 发送 ────────────────────────────────────────────

    def write(self, data: bytes) -> bool:
        """写入串口。成功返回 ``True``，失败时自动关闭连接。"""
        try:
            self.serial_port.write(data)
            return True
        except Exception:
            self.close()
            return False

    # ── 接收（回调驱动，不依赖 Tkinter） ────────────────

    def start_receiving(
        self,
        on_data: Callable[[bytes], None],
        on_count: Callable[[int], None],
        on_disconnect: Callable[[], None],
    ) -> None:
        """启动后台接收线程。

        参数
        ----
        on_data : (bytes) -> None
            收到数据时回调。
        on_count : (int) -> None
            字节计数更新时回调。
        on_disconnect : () -> None
            串口异常断开时回调。
        """
        self._rx_active = True
        self._rx_thread = threading.Thread(
            target=self._rx_loop,
            args=(on_data, on_count, on_disconnect),
            daemon=True,
        )
        self._rx_thread.start()

    def _rx_loop(
        self,
        on_data: Callable[[bytes], None],
        on_count: Callable[[int], None],
        on_disconnect: Callable[[], None],
    ) -> None:
        """后台线程：循环读取串口数据并分发到回调。"""
        total = 0
        while self._rx_active and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    if data:
                        total += len(data)
                        on_data(data)
                        on_count(total)
                else:
                    time.sleep(0.01)      # 避免忙等导致 CPU 100%
            except Exception:
                on_disconnect()
                break

# -*- coding: utf-8 -*-
"""
常量定义
========

按键过滤集合、串口参数枚举值。
"""

import serial

# ── 按键过滤 ──────────────────────────────────────────────
# 这些键按下时不产生可打印字符，在键盘转发模式下直接忽略

_MODIFIER_KEYS = {
    "Shift_L", "Shift_R", "Control_L", "Control_R",
    "Alt_L", "Alt_R", "Caps_Lock", "Num_Lock", "Scroll_Lock",
    "Super_L", "Super_R", "Menu", "Multi_key",
}
_NAV_KEYS = {
    "Home", "End", "Up", "Down", "Left", "Right",
    "Prior", "Next", "Insert", "Delete",
}
_FUNC_KEYS = {f"F{i}" for i in range(1, 13)}
SKIP_KEYS = _MODIFIER_KEYS | _NAV_KEYS | _FUNC_KEYS

# ── 串口参数枚举值（PySerial 常量） ──────────────────────

DATA_BITS_OPTS = [
    ("5", serial.FIVEBITS),
    ("6", serial.SIXBITS),
    ("7", serial.SEVENBITS),
    ("8", serial.EIGHTBITS),
]

PARITY_OPTS = [
    ("None",  serial.PARITY_NONE),
    ("Odd",   serial.PARITY_ODD),
    ("Even",  serial.PARITY_EVEN),
    ("Mark",  serial.PARITY_MARK),
    ("Space", serial.PARITY_SPACE),
]

STOP_BITS_OPTS = [
    ("1",   serial.STOPBITS_ONE),
    ("1.5", serial.STOPBITS_ONE_POINT_FIVE),
    ("2",   serial.STOPBITS_TWO),
]

# ── 波特率预设 ────────────────────────────────────────────

BAUD_PRESETS = [
    "9600", "19200", "38400", "57600",
    "115200", "230400", "460800", "921600",
]

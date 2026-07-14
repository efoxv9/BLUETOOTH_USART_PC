# -*- coding: utf-8 -*-
"""
USB-USART 键盘转发器 & 串口调试助手
====================================

功能:
  1) 键盘转发模式 —— 在发送区打字，按键内容立即逐字节转发到串口
  2) 串口调试模式 —— 显示接收数据，支持 HEX / ASCII 切换
  3) 完整串口参数配置 —— 数据位 / 校验位 / 停止位 / 波特率

运行:
  pip install pyserial
  python -m usart_keyboard

打包:
  pip install pyinstaller
  pyinstaller --onefile --windowed --name USART_Keyboard src/usart_keyboard/__main__.py
"""

from usart_keyboard.app import USARTKeyboardApp


def main() -> None:
    """应用程序入口。"""
    import tkinter as tk

    root = tk.Tk()
    USARTKeyboardApp(root)
    root.mainloop()

# USB–USART Keyboard Transponder & Serial Debug Terminal

A lightweight cross-platform desktop utility that performs real-time keyboard-to-USART transduction. Each keystroke is forwarded byte-by-byte via the serial interface immediately upon pressing, eliminating the conventional compose-then-send workflow. The system also functions as a general-purpose serial debug terminal supporting both hexadecimal and ASCII data presentation for bidirectional communication.

> 轻量级跨平台桌面工具，实现键盘到 USART 串口的实时转发。按下的每个按键即刻逐字节转发，免去传统的编写再发送流程。同时可作为通用串口调试终端，支持 HEX 与 ASCII 数据显示。

---

## Screenshot

```text
┌──────────────────────────────────────────────┐
│ COM端口: [▼ COM3 — USB Serial ] 波特率:[▼ 115200] [刷新] [关闭连接]│
│  状态: ● 已连接 — COM3 @ 115200 baud          │
│ ───────────────────────────────────────────── │
│ 在此窗口按键，内容将转发到 USART:                │
│ ┌──────────────────────────────────────────┐  │
│ │ hello world!                             │  │
│ │ AT+GMR\r\nOK                             │  │
│ └──────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

## Project Structure

```text
src/
└── usart_keyboard/
    ├── __init__.py           # Package entry point, exports main()
    ├── __main__.py           # python -m invocation target
    ├── app.py                # Main window UI and event handling
    ├── constants.py          # Application-wide constants
    └── serial_manager.py     # Serial port abstraction layer
├── pyproject.toml            # Package metadata and build configuration
├── .gitignore
├── README.md
└── requirements.txt
```

> 包入口导出 `main()` 函数；`__main__.py` 支持 `python -m` 调用；三个核心模块分别负责界面、常量和串口抽象层；`pyproject.toml` 记录元数据与构建配置。

## Architecture

The software is organised as a modular Python 3 package following the standard `src/` layout. The architecture comprises three principal components:

**`serial_manager.py`** — Encapsulates all serial port operations including device enumeration, connection lifecycle management, asynchronous data reception via a daemon thread, and byte-level transmission. This module is entirely independent of the GUI framework, communicating with the presentation layer exclusively through callback functions.

**`app.py`** — Implements the main application window using the Tkinter toolkit. Responsible for widget construction, event binding, and coordinating user input with the serial manager.

**`constants.py`** — Defines key-filtering sets (modifier, navigation, function keys) and serial parameter enumerations (data bits, parity, stop bits, baud rate presets).

> 软件按照标准 `src/` 布局组织为模块化 Python 3 包。`serial_manager.py` 封装全部串口操作，完全独立于 GUI 框架，仅通过回调表现层通信。`app.py` 基于 Tkinter 实现主窗口与事件处理。`constants.py` 定义按键过滤集合与串口参数枚举。

## Hardware Prerequisites

A USB-to-USART bridge module (CH340, CP2102, FT232, or equivalent) is required to connect the host computer with the target embedded device. The electrical connection must follow the cross-wiring convention:

```text
Host USB ──USB cable──> [USB–TTL Bridge] ──TX──>  Target RX
                                    │         ──RX──>  Target TX
                                    │         ──GND──> Target GND
                              (CH340/CP2102/FT232)
```

> 需要一个 USB 转 USART 桥接模块连接主机与目标设备。电气连接务必遵循交叉接线规则：模块 TX 接设备 RX，RX 接 TX，GND 接 GND。TX→TX 直连会导致通信失败。

## Installation and Execution

### Pre-built Executable (Windows Only)

A standalone Windows executable is available at `dist/USART_Keyboard.exe`. This binary operates without a Python runtime and may be launched by double-click.

> Windows 用户可直接运行 `dist/USART_Keyboard.exe`，无需 Python 环境。

### Source Code Execution

**Runtime dependencies:**

- Python 3.10 or later
- pyserial ≥ 3.5

**Procedure:**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run as a module (recommended)
python -m usart_keyboard

# 3. Alternatively, install and run as a command
pip install -e .
usart-keyboard
```

> 安装 `pyserial` 依赖后通过 `python -m usart_keyboard` 启动。也可 `pip install -e .` 安装到环境，之后在命令行直接输入 `usart-keyboard`。

### Packaging as Standalone Executable

For environments lacking a Python interpreter, PyInstaller may be used to produce a single executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name USART_Keyboard src/usart_keyboard/__main__.py
```

The resulting binary resides at `dist/USART_Keyboard.exe`.

> 可使用 PyInstaller 将应用打包为单个 exe 文件，适用于无 Python 环境的目标机器。

## Usage Instructions

1. Connect the USB-to-serial adapter and confirm the driver is correctly installed.
2. Launch the application with `python -m usart_keyboard`.
3. Select the enumerated serial port from the COM dropdown (e.g., `COM3 — USB-SERIAL CH340`). Click the refresh button if the list is empty.
4. Set the baud rate to match the target device (115200 is the most common for embedded applications).
5. Optionally adjust data bits (default: 8), parity (default: None), and stop bits (default: 1).
6. Click "打开连接" (Open Connection). The status indicator transitions from red (● 未连接) to green (● 已连接), confirming a successful link.
7. Type in the lower text area. Each keystroke is forwarded via the serial interface immediately.
8. Click "关闭连接" (Close Connection) to release the serial port upon completion.

> 插入 USB 转串口模块并确认驱动正常 → 启动程序 → 选择对应串口 → 设置与目标设备一致的波特率 → 可选调整数据位/校验位/停止位 → 点击"打开连接"建立连接 → 在发送区打字即可转发 → 使用完毕后关闭连接。

### Key Mapping

| Input | Transmitted Sequence | Remarks |
| --- | --- | --- |
| Alphanumeric characters | Corresponding UTF-8 bytes | Direct pass-through |
| Enter | `\r\n` (0x0D 0x0A) | Carriage Return + Line Feed |
| Tab | `\t` (0x09) | Horizontal tabulation |
| Escape | `\x1b` (0x1B) | ESC control character |
| Backspace | `\x08` (BS) | Backspace control character |
| Ctrl / Alt / Shift / Fn / Arrow | *Not transmitted* | Filtered by `_SKIP_KEYS` set |

> 字母数字键直通发送 UTF-8 字节；Enter 发送 CR+LF；Tab、Escape、Backspace 发送对应控制字符；修饰键和导航键被常量集合过滤，不发送任何数据。

## HEX Transmission and Reception

The application provides hexadecimal data exchange capability. Users may compose raw byte sequences as space-separated hexadecimals (e.g., `41 42 43` or `414243`) in the HEX entry widget and transmit them via the "发送 HEX" button or the Return key. On the receiving end, toggling "HEX 显示" switches the display mode from UTF-8 decoded text to space-delimited two-character hexadecimal notation (e.g., `48 65 6C 6C 6F`).

> 程序支持 HEX 数据收发。在 HEX 输入框中以空格分隔的十六进制字节序列（如 `41 42 43`）输入后点击"发送 HEX"或回车发送。接收区的"HEX 显示"开关可在 UTF-8 文本与双字符十六进制表示之间切换。

## Frequently Encountered Issues

**The COM port dropdown is empty.**  
Confirm that the USB-to-serial adapter is physically connected and the driver is installed. Check the system device manager (Windows) or run `lsusb` (Linux). Click the refresh button to re-enumerate.

> 下拉框为空 — 确认模块已插入且驱动正常。Windows 下查看设备管理器，Linux 下运行 `lsusb`。点击"🔄 刷新"重新枚举。

**Connection fails with an error dialog.**  
The serial port may be occupied by another application, or the user may lack sufficient permissions (on Linux, access to `/dev/ttyUSB*` ordinarily requires membership in the `dialout` group).

> 连接失败 — 端口可能被其他程序占用，或权限不足（Linux 下需加入 `dialout` 组）。

**The target device does not respond to transmitted characters.**  
Investigate the following in order: baud rate mismatch, incorrect TX/RX wiring (observe the cross-connection rule), and whether the device UART is enabled. A methodical approach is to first confirm device responsiveness using a known-working serial terminal.

> 设备无响应 — 依次排查：波特率是否匹配、TX/RX 接线是否交叉（TX→RX）、设备 UART 是否启用。建议先用其他串口工具排除硬件故障。

## License

This project is distributed under the MIT License.

> 本项目基于 MIT 许可证发布。

# BitMaster Pro (BOS Calculator)

BitMaster Pro is an advanced bitwise calculator and visualizer designed specifically for **System Software Engineers** and firmware developers. It provides a visual, interactive, and fast way to work with hardware registers, understand memory layout, and manipulate bit fields.

## Features

- **Interactive 64-bit Visualizer:** Provides a real-time UI showing the state of bits 0-63. Click any bit to toggle it instantly.
- **Data Width Selection:** Work with 8-bit, 16-bit, 32-bit, or 64-bit bounds. Automates truncation and overflow testing.
- **Advanced Data Views:**
  - **Decimal, Hexadecimal, Binary** representations.
  - **Signed Integer:** Translates values using 2's Complement based on selected width.
  - **Float (IEEE 754):** Decodes hex payload as Floating point values (32-bit `float` / 64-bit `double`).
  - **ASCII:** Decodes payloads for packet header and memory string debugging.
- **Endianness Swap:** Instantly swap between Big Endian and Little Endian formats (e.g. `0xAABB` <-> `0xBBAA`).
- **Expression Calculator:** Supports evaluating full bitwise expressions (e.g. `0xC00 | (1<<5) & ~0xF`).
- **Bit Field Extractor:** Input Start/End boundaries to easily extract and mask specific bit ranges from a complex register.
- **Quick Toggle Bit:** Need to instantly flip bit 31? Type "31" in the Quick Toggle box and press Enter.
- **History Tracking:** The main input is a combobox that remembers your last calculated expressions.
- **Theme Persistence:** Toggle between Dark and Light mode. Your preference is saved locally (`config.json`) and persists across runs.

## Keyboard Shortcuts

- `Ctrl + F` : Focus on the Main Expression Input
- `Ctrl + S` : Focus on the 'Quick Toggle Bit' Input
- `Ctrl + R` : Reset Value to 0

## Installation

BitMaster Pro is built using Python completely locally. It requires `customtkinter`.

```bash
pip install customtkinter
```

You can run it directly using:
```bash
python bitmaster.py
```

### Build Executable
If you want to create a standalone `.exe` without needing a Python environment, install PyInstaller:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --clean --name "Calculator_BOS_v3" --icon="calculator.ico" bitmaster.py
```
The standalone executable will be generated inside the `dist/` directory.

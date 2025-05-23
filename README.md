# Win95 Style Python Application

This project is a Windows 95 style desktop environment application built with Python and PyQt5. It includes several classic apps such as Calculator, Notepad, Paint, and Explorer, all styled to mimic the Windows 95 look and feel.

## Features

- Windows 95 style UI with custom window frames and controls
- Dynamically generated colorful icons using Pillow
- Multiple apps: Calculator, Notepad, Paint, Explorer
- Sound effects using pygame
- Easy to run and package as an executable

## Running the Application

1. Ensure you have Python 3.7+ installed.
2. Install required dependencies:
   ```
   pip install PyQt5 pygame Pillow
   ```
3. Run the main application:
   ```
   python main.py
   ```

## Packaging as Executable

To create a Windows executable using PyInstaller:

1. Install PyInstaller if not already installed:
   ```
   pip install pyinstaller
   ```
2. Build the app in a folder with dependencies:
   ```
   pyinstaller --onedir --windowed --name "Win95App" main.py
   ```
3. Test the executable in the `dist/Win95App` folder.
4. Optionally, create a single bundled executable:
   ```
   pyinstaller --onefile --windowed --name "Win95App" main.py
   ```
5. If you have additional data files, include them with `--add-data` option.

## Notes

- Icons are generated dynamically; no external icon files are required.
- Sound effects require pygame mixer to be initialized properly.
- The app is designed for Windows but may run on other platforms with PyQt5 support.

## License

This project is provided as-is without warranty. Feel free to modify and use it as you like.

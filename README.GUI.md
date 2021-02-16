# Graphical User Interface

## Information

The GUI is developed with `qt5` library and is wrapped as a single executable with `pyinstaller`. Although the following documentation refers to building and executing the application under Windows, it's possible to build executables for other operating systems(Linux and macOS).

## Run

### Run Requirements

You might need to install [Microsoft Visual C++ Redistributable package](https://support.microsoft.com/en-us/topic/the-latest-supported-visual-c-downloads-2647da03-1eea-4433-9aff-95f26a218cc0) for some Windows versions.

### Start

You don't need to install the application or run the application as an administrator user. However, some Antivirus programs might report it as a virus. The executables shared with each release is not signed and that's the reason for the virus warning. If you have doubts about the application security, you can build the source code.

## Build

### Requirements

All requirements for building the main application are required for building the GUI.

1. You need to install requirements under *Run Requirements* section.
2. In order to install the main application requirements you need to install Build Tools for Visual Studio from [here](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16).

### Build steps

1. Open Command Prompt or PowerShell.
2. Navigate to the root of the application repository.
3. Install main application requirements via:
```console
$ pip install -r requirements.txt
```
4. Install GUI requirements via:
```console
$ pip install -r requirements.gui.txt
```
5. Build via:
```console
$ python -m PyInstaller gui.spec
```
6. The GUI `.exe` file will be located under `dist` directory. In order to debug the app, you can start it via the CLI.

### Adding support for new parsers

In order to add support for a new parser, you need to list the parser manually into `libs\process.py` file in the `supported_parsers` dictionary.

### Generate new spec file

You can generate new pyinstaller spec file via:
```console
$ python -m PyInstaller --name "NAP Stocks Calculator" --clean --onefile --noconfirm --hidden-import="libs.parsers" --hidden-import="libs.parsers.*" ".\revolut-stocks\libs\gui\main.py"
```

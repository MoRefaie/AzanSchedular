# AzanSchedular

AzanSchedular is a cross-platform application that automates the scheduling and playback of Islamic prayer times (Azan) on various devices. It features a robust Python backend for scheduling and device management, and a modern React-based UI for configuration and monitoring.

## Features

- Automated Azan scheduling based on location and prayer times
- Device management (including Apple devices)
- Custom audio support
- Support for Modern, responsive UI via APIs
- Easy configuration and monitoring
- Cross-platform executable builds

## Tech Stack

- **Backend:** Python, FastAPI, PyInstaller
- **Frontend:** React, TypeScript, Tailwind CSS, Vite
- **Build:** GitHub Actions, pkg

## Installation

### Backend

```sh
cd AzanSchedular
pip install -r requirements.txt
python azan_app.py
```

## Usage

- Configure prayer times and devices via the UI.
- Scheduler runs in the background and plays Azan at the correct times.

## Build

See [build.bat](build.bat) or use the provided GitHub Actions workflow.


## License

[MIT](../License.txt)

## Contact

For questions or support, open an issue or contact [Refaie.moh@gmail.com](mailto:refaie.moh@gmail.com).
# AzanSchedular

AzanSchedular is a cross-platform application for managing and scheduling Azan (Islamic prayer calls) with a modern UI, system tray integration, and robust scheduling features.

![Build Status](https://img.shields.io/github/actions/workflow/status/MoRefaie/AzanSchedular/python-app.yml?branch=main)
![License](https://img.shields.io/github/license/MoRefaie/AzanSchedular)

## Features

- FastAPI backend for API and scheduling
- Modern web UI (Node.js, Vite, Tailwind)
- System tray integration (pystray)
- Configurable prayer times and notifications
- Cross-platform support (Windows, Linux, Mac)

## Architecture

```
+-------------------+      +-------------------+      +-------------------+
|   Azan UI (Web)   | <--> |    FastAPI API    | <--> |   Scheduler Core  |
+-------------------+      +-------------------+      +-------------------+
        ^                        ^                            ^
        |                        |                            |
        +------------------------+----------------------------+
                         System Tray (pystray)
```

## Quick Start

```bash
# Clone the repo
$ git clone https://github.com/MoRefaie/AzanSchedular.git
$ cd AzanSchedular

# Install Python dependencies
$ pip install -r requirements.txt

# Run the backend
$ python azan_app.py

# (Optional) Run the UI
$ git clone https://github.com/MoRefaie/AzanUI.git
$ cd AzanUI
$ npm install
$ npm run dev
```

## Configuration

- Edit `AzanSchedular/config/system.json` for API and UI settings.
- Use environment variables for secrets in production.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See [License.txt](License.txt).

## FAQ

- **How do I add a new prayer time calculation method?** See the scheduler module and extend `prayer_times_fetcher.py`.
- **How do I run tests?** `pytest` in the root directory.

## Troubleshooting

- Check logs in `AzanSchedular/logs/` for errors.
- Ensure all dependencies are installed and ports are available.

---

For more details, see the code and open an issue if you have questions!
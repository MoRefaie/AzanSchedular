# AzanScheduler

AzanScheduler is a cross-platform application for managing and scheduling Azan (Islamic prayer calls) with a modern UI, system tray integration, and robust scheduling features.

![Build Status](https://img.shields.io/github/actions/workflow/status/MoRefaie/AzanScheduler/AzanScheduler-Build.yml)
![Latest Release](https://img.shields.io/github/v/release/MoRefaie/AzanScheduler)
![License](https://img.shields.io/github/license/MoRefaie/AzanScheduler)

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
$ git clone https://github.com/MoRefaie/AzanScheduler.git
$ cd AzanScheduler

# Install Python dependencies
$ pip install -r requirements.txt

# Run the backend
$ python AzanScheduler/azan_app.py

# (Optional) Run the UI
$ git clone https://github.com/MoRefaie/AzanUI.git
$ cd AzanUI
$ npm install
$ npm run dev
```

## Configuration

- Edit `AzanScheduler/config/system.json` for API and UI settings.
- Use environment variables for secrets in production.

## Logs & Media

- Logs are stored in `AzanScheduler/logs/`.
- Media files (icons, audio) are in `AzanScheduler/media/`.

## Tests

- Place your test files in the `tests/` directory at the project root.
- Run tests with:
  ```bash
  pytest
  ```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See [License.txt](License.txt).

## FAQ

- **How do I add a new prayer time calculation method?** See the scheduler module and extend `AzanScheduler/prayer_times_fetcher.py`.
- **How do I run tests?** `pytest` in the project root.

## Troubleshooting

- Check logs in `AzanScheduler/logs/` for errors.
- Ensure all dependencies are installed and ports are available.

---

For more details, see the code and open an issue if you have questions!
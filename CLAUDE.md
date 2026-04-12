# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Kivy-based touchscreen kalendar/dashboard app for a Raspberry Pi. Displays clock, calendar, weather (OpenWeatherMap), and Todoist tasks. Czech locale. Entry point: `main.py`. Launched on the Pi via `run.sh`.

Note: `pyproject.toml` pins `python = "3.7.*"` (Pi target). Global user instructions say "use 3.12 unless project states otherwise" — this project states otherwise. Stay 3.7-compatible (no `match`, no PEP 604 unions, etc.).

## Run / dev

- Run app: `poetry run python3 main.py` (needs `.env` with `TODOIST_URL`, `TODOIST_TOKEN`, `WEATHER_TOKEN`).
- `rpi_backlight` import is wrapped in try/except — app falls back to `BlacklightDummy` on non-Pi dev machines.
- Type check: `poetry run mypy .` (config in `mypy.ini`).
- No test suite exists; no lint config beyond mypy.

## Architecture

Three loosely-coupled layers wired together in `main.py`:

1. **Data providers** (`todoist/`, `weather/`) — long-lived objects that poll external APIs via `kivy.network.urlrequest.UrlRequest` on a `Clock.schedule_interval`. Each exposes `run()`, `stop()`, `add_subscriber()`. They cache last response and only notify subscribers on change.
   - `todoist.ComposeTodoist` merges multiple `Todoist` sources (currently `Birthdays` from `birthdays.txt` + `KivyTodoist` REST). It owns a per-source cache and re-merges on every notification.
   - `weather.OpenWeather` fetches both current weather and forecast; subscribers are dicts keyed by `InfoType.Weather` / `InfoType.Forecast`.

2. **Global registry** (`globals.py`) — `set_global` / `get_global` keyed by module-level `uuid.uuid4()` constants (`TODOIST_KEY`, `WEATHER_KEY`). Widgets retrieve providers via these keys instead of constructor injection. When adding a new provider, follow the same UUID-key pattern.

3. **Kivy UI** (`widgets/`, `pitime.kv`) — root is `AppWidget` (`BoxLayout`) defined in `pitime.kv`. Layout: `CalendarWidget` on the left, `CarouselWidget` on the right. The carousel cycles `MainScreenWidget` / `TasksWidget` / `ForecastWidget` and auto-returns to main after `return_delay` seconds. Widgets subscribe to providers in `__init__` via `get_global(...).add_subscriber(self.update_xxx)`.

`.kv` files live next to their `.py` widget. `pitime.kv` is auto-loaded by Kivy from the `PiTimeApp` class name.

## Conventions specific to this repo

- Pydantic v2 models in `todoist/interface.py` use `extra="allow"` + `populate_by_name=True` and field aliases to map the Todoist Sync-API payload onto REST-style names. Preserve aliases when adding fields.
- Widgets are constructed in Python (see `MainScreenWidget.__init__`) rather than declared in `.kv` — both styles coexist; match the surrounding widget's style.
- Fonts in `fonts/` are registered by name in `main.py` (`Roboto-Black`, `Roboto-Light`, `tahoma`, `meteocons`) and referenced from `.kv` files.
- Czech locale (`cs_CZ.UTF-8` / `Czech_Czech Republic.1250`) is set at startup; UI strings are Czech.

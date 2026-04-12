# Code Review — kalendar

## Architecture / design

**1. Global registry is service-locator antipattern.** `globals.py` + UUID keys (`TODOIST_KEY`, `WEATHER_KEY`) hide dependencies. Widgets reach into a process-wide dict from their `__init__` (`MainScreenWidget`, `MonthTable`, `TasksListWidget`, `WeatherWidget`, `ForecastWidget`). Result: every widget is untestable in isolation, init order is implicit, and `get_global()` can return `None` — half the call sites check, half don't (`MainScreenWidget` doesn't, `MonthTable` does). Pass providers explicitly down the tree, or use Kivy's `App.get_running_app()` and stash them on the App. The UUID keys add zero safety over plain string keys, just obfuscation.

**2. `Todoist` "interface" is faux-OOP.** `interface.py:71` defines a base class with `raise NotImplementedError` stubs, but `ComposeTodoist` (`compose.py:9`) doesn't even inherit from it — it just duck-types. Either commit to `abc.ABC` + `@abstractmethod`, or drop the base class and rely on the protocol. Current state is the worst of both worlds.

**3. ComposeTodoist breaks the contract.** It claims to be a `Todoist` but `close_task` calls `close_task` on *every* sub-provider (`compose.py:30`) — including `Birthdays`, which is a no-op only by accident. If a real second source were added, you'd close tasks in providers that don't own them. The merge logic also resorts the merged list on every notification but `KivyTodoist` already pre-sorts its own — wasted work and inconsistent ordering keys (`KivyTodoist` sorts by `due.date`, `ComposeTodoist` by `(priority, due)`).

**4. Pub-sub is reinvented three times** (`KivyTodoist`, `Birthdays`, `OpenWeather`, `ComposeTodoist`) with subtly different signatures (`Callable` vs `Dict[InfoType, Callable]`). One small `Observable[T]` helper would kill ~40 lines of duplication. No `remove_subscriber` anywhere — widgets subscribed in `__init__` leak forever if rebuilt.

**5. Polling cadences make no sense.** `KivyTodoist` polls Todoist every **10 seconds** (`main.py:64`, `kivytodoist.py:19`). That's ~8,600 requests/day for a calendar widget. Birthdays reads a static text file every **10 seconds** (`birthdays.py:12`). Weather every 60 s is borderline reasonable but still over-eager — OpenWeatherMap free tier updates ~10 min. Bump these to minutes/hours.

## Bugs / correctness

**6. `OpenWeather.update` discards `UrlRequest` references.** `req1`/`req2` are local and unused (`openweather.py:40-59`). On a slow Pi these can be GC'd before completion in some Kivy versions; even if not, the leading underscore convention is missing and the assignments are dead code.

**7. `ForecastWidget.update_forecast` has a `print()`** (`forecast.py:65`). Debug leftover.

**8. Timezone is wrong.** `forecast.py:56-61` localizes the timestamp to UTC and then comments out the actual conversion to Europe/Prague — so labels are off by 1–2 h depending on DST. Just use `dt.datetime.fromtimestamp(timestamp, tz=ZoneInfo("Europe/Prague"))`. Drop pytz entirely; `zoneinfo` is stdlib.

**9. Kelvin → Celsius is `- 273`, not `- 273.15`.** Five places: `weather.py:34,44,53`, `forecast.py:69`. Off by ~0.15 °C every reading. Worse: `int(temp) - 273` (truncates first, then subtracts) is different from `int(temp - 273.15)`. Pick one and centralize it (`def kelvin_to_c(k): return k - 273.15`).

**10. `Birthday.from_string`** (`birthdays.py:55-60`) calls `dt.datetime.now()` three times in three lines and uses naive comparison. On New Year's Eve at 23:59:59.5 the three calls can straddle midnight — a real (if rare) bug. Capture `now = dt.datetime.now()` once. Also, `replace(year=...)` blows up on Feb 29.

**11. `MonthTable.set_tasks`** (`calendar.py:126`) iterates `self.children` which Kivy reverses; works here only because `task` is set on every `DayWidget` regardless of order. Fragile; comment or use `walk(restrict=True)`.

**12. `DateWidget.set_due`** (`tasks.py:111`) reads `due.string` even when `due.date` is falsy — but the `if` block only sets `bg_color` inside the branch. If `due.date` is empty, `bg_color` retains the previous task's value. Reset it.

**13. `Task` model uses `Field(alias=...)`** (`interface.py:53,56,60,61,62,63,64`) but `populate_by_name=True` — fine — except `_split_date_and_datetime` mutates `data` to add `datetime` only if absent, and the `due.date` field then contains *only* the date portion. Roundtripping a model with `model_dump()` and re-validating will silently change behavior. Add a unit test.

**14. `KivyTodoist._on_success` re-raises after logging** (`kivytodoist.py:59`), which propagates into Kivy's `UrlRequest` callback and gets swallowed anyway. Either log + return, or don't catch.

## Style / Python

**15. CLAUDE.md says single quotes nowhere — use double.** The codebase is ~95% single quotes (`'vertical'`, `'STARTING REGULAR ...'`, etc.). Run `ruff format` once and be done.

**16. `import typing as tp` / `import datetime as dt` / `import dataclasses as dc` — partially followed.** `forecast.py`, `weather.py`, `clock.py`, `calendar.py` follow it; `interface.py` (todoist) does too but also does `from pydantic import ...` inline mid-file order is fine. `viewer.py` and `main.py` don't. Pick one rule and apply it.

**17. String-quoted forward refs everywhere** (`'tp.Callable[[Todos], None]'`, `'tp.Optional[CurrentWeather]'`). Python 3.7 doesn't need these for runtime — `from __future__ import annotations` would let you drop every quoted annotation in the file.

**18. Dead code rot.** `viewer.py` looks abandoned. `calendar.py` has 20+ lines of commented-out code (`CircleSettings`, `_next_update` variants, `_update_min_width`). `forecast.py` has commented graph code. `weather.py` has commented `mean()` calls. `from statistics import mean` is unused. Delete or move to a branch.

**19. Numeric literal magic.** `0x88 / 256` in `tasks.py:115` (should be `/255` for 8-bit; `/256` is wrong by ~0.4%). `min(7, max(0, day_diff)) / 7 * max_light` would read better as `clamp(day_diff, 0, 7) / 7 * max_light` with a one-line helper.

**20. Bare `pass` after `except ImportError`** (`viewer.py:108`) followed by an unconditional error log on the next line — the `try` does nothing useful.

**21. `ListProperty([])`, `ObjectProperty(None)` declared but never used** in `WeatherWidget` (`forecast_1h`, `forecast_3h` are set from kv though; but `temperatures` in `ForecastWidget:33` is never read).

**22. `BlacklightDummy` is created twice** (`main.py:24,33`) under different names (`Blacklight` vs `BlacklightDummy`) — typo. Line 24 sets `Blacklight` but line 31 references `Backlight`. The whole try/except dance is duplicated at module level *and* class level. Single `try/except` at module level, then `backlight = ObjectProperty(Backlight() if HAS_BACKLIGHT else BlacklightDummy())`.

## Performance

**23. `MonthTable.show_month_of_date` rebuilds 42 widgets every midnight** (`calendar.py:117-124`). Fine. But `set_tasks` is called on every Todoist poll (every 10 s), each time linearly scanning all `DayWidget` children and calling `embellish()` → `canvas.before.clear()` → recreate `Rectangle`/`Line` for cells whose `task` flag didn't actually change. Cache the previous value and short-circuit `task.setter`.

**24. `TasksListWidget.update_tasks` clears and rebuilds every `TaskWidget` from scratch** on every poll, even if nothing changed. `KivyTodoist` already does the equality check upstream — but `ComposeTodoist` doesn't, so this widget *will* re-render every 10 s. Diff or hash check.

**25. `Birthdays` reads the file from disk every 10 s** when the contents change ~once a year. Use `os.stat().st_mtime` to skip unchanged reads, or just load once at startup and rerun on date rollover.

**26. `pytz` import in `forecast.py` for one timezone lookup** — pulls a 500 KB dependency. Use `zoneinfo` (3.9+) or, for 3.7, `backports.zoneinfo` if you really need historical TZ data, which you don't here.

**27. Pydantic v2 model construction in hot paths** is fine but `extra="allow"` keeps every junk field from the API in memory. Switch to `extra="ignore"` unless you actually use the extras (you don't appear to).

## Project hygiene

**28. `pyproject.toml` says Python 3.7.\*** — EOL for 2.5 years. The Pi can run 3.11+ today via `pyenv` or Raspberry Pi OS Bookworm. Upgrade and you get `zoneinfo`, `match`, walrus, dataclass `kw_only`, etc.

**29. `output.log` (18 KB) and a stray file named `1` (18 KB, identical size) are committed-adjacent untracked.** `.gitignore` excludes `*.log` but `1` is just garbage. `.weatherwidget.py.swp` is a leftover vim swap. Clean and add `*.swp` to `.gitignore`.

**30. No tests at all.** `pyproject.toml` doesn't even have pytest. The pydantic models, the Birthday parser, and `Compose._merge_todos` are all pure-logic and trivially testable.

**31. `mypy.ini` exists but `mypy` reports unknown amount of errors — no CI, no pre-commit.** The `_split_date_and_datetime` validator returns `Any`, and several `-> None` annotations are wrong (`OpenWeather._on_success_handler` is annotated `-> None` but returns a callable — `mypy` should be screaming).

**32. `poetry.lock` committed with Python 3.7 deps.** Locked to ancient `kivy 2.1.0`, `pydantic 2.5.1`. Bump.

**33. `run.sh` calls `/home/pi/scripts/day.sh`** — undocumented external dependency. At least drop a comment in the README (which doesn't exist) or in `run.sh`.

## What I'd do differently (priority order)

1. **Kill `globals.py`.** Pass `todoist`/`weather` into `AppWidget(__init__)` and down via constructor args or `App.get_running_app()`.
2. **Fix the polling intervals.** Todoist 5 min, birthdays once + on-date-change, weather 10 min.
3. **Centralize Kelvin→Celsius and timezone conversion** in one helper module; use `zoneinfo`.
4. **Replace the three pub-sub implementations** with one generic `Observable[T]` (~15 lines).
5. **Bump Python to 3.11+**, drop quoted annotations, drop `pytz`.
6. **Delete `viewer.py`** and all commented-out code, or move to a `dev/` branch.
7. **Add a handful of pytest tests** for `Birthday.from_string`, `Task` parsing from a real Todoist payload fixture, and `ComposeTodoist._merge_todos`.
8. **Make `set_tasks` / `update_tasks` idempotent** (skip work if state unchanged) — biggest perf win on a Pi.
9. **Either delete the `Todoist` base class or make it `abc.ABC`** and inherit from it everywhere including `ComposeTodoist`.
10. **Add `ruff` + `mypy --strict`** to a pre-commit hook; fix what falls out.

Nothing here is catastrophic — the app is small enough that a weekend of cleanup would fix the lot. The main thread to pull is the global registry: untangling that forces honest dependencies and makes everything else easier to test.

# Rust rewrite — implementation plan

Stack: **Slint** (UI) + **tokio** (async runtime) + **reqwest** (HTTP) + **serde** (JSON) + **jiff** or **chrono** (dates) + **dotenvy** (env). Render backend: **linuxkms** on the Pi (no X11), **winit** on your dev machine.

The hard parts of this project, in order: (1) bridging async tasks to the Slint event loop, (2) cross-compiling or remote-building for the Pi, (3) Slint's model/property system for dynamic lists. The rest is just typing.

## Step 0 — Environment and toolchain

**Do:**
- `rustup` stable, add target `aarch64-unknown-linux-gnu` (assuming 64-bit Raspberry Pi OS — check with `uname -m` on the Pi; if `armv7l`, use `armv7-unknown-linux-gnueabihf`).
- Install `cross` (`cargo install cross`) — runs cross-compilation inside Docker, saves you from sysroot pain.
- Verify you can build, scp, and run a "hello world" binary on the Pi. Do this *before* writing real code.
- Decide dev loop: edit on host, cross-compile, scp, run via SSH. Compiling on the Pi 3A itself is technically possible but painful (512 MB RAM will swap hard on any non-trivial crate graph).

**Learn:**
- `cross` README — it's short.
- Rust target triples: one paragraph in the rustup book.

## Step 1 — Hello Slint

**Do:**
- `cargo new --bin kalendar` inside `rust/`.
- Add `slint = "1"` and follow Slint's "Getting Started" to show an empty window with a `Text { text: "hello"; }`.
- Run it on your dev machine with the default backend (winit). Don't touch the Pi yet.

**Learn:**
- Slint "Getting Started" tutorial (the Memory Game walkthrough is 30 min and teaches the property/callback model — do it end-to-end, don't skim).
- Key concepts: `.slint` files are compiled at build time by `slint-build` in `build.rs`; the generated Rust type is a `ComponentHandle`; you read/write properties via `set_*`/`get_*` and wire callbacks via `on_*`.

## Step 2 — Static layout port

**Do:**
- Reproduce the visible structure of the current app in `.slint`, all static placeholders, no data yet:
  - Root `HorizontalLayout`: left pane (calendar column), right pane (content switcher).
  - Left: big day-number, day-of-week, month-year, 6×7 grid of day cells.
  - Right: switchable views (main/tasks/forecast). Kivy's `Carousel` has no Slint equivalent — model it as an `in property <int> current-view;` plus three components shown/hidden via `visible:` or a `states { }` block. Touch-swipe can come later.
- Hardcode strings so you can see the layout at size 800×480 (or whatever your DSI screen is).

**Learn:**
- Slint layouts: `HorizontalLayout`, `VerticalLayout`, `GridLayout`.
- Slint `states`/`transitions` syntax (for the view switcher).
- Property bindings and how child components expose `in`/`out`/`in-out` properties.

## Step 3 — Data models and parsing (pure, no I/O)

**Do:**
- Define Rust structs: `Task`, `Due`, `CurrentWeather`, `Forecast`, `WeatherEntry`. Derive `Deserialize`. Use `Option<T>` for nullable fields. Mark extra fields `#[serde(default)]` or just ignore them (don't copy `extra="allow"`).
- Write one pure function `parse_todoist_response(&str) -> Result<Vec<Task>>` and one for OpenWeatherMap.
- Write the birthday parser (`birthdays.txt` → `Vec<Task>`) as a pure function. Keep date math in one place.
- Capture a real response from each API to `tests/fixtures/*.json`, write unit tests that parse them. This gives you a fast inner loop with zero network.

**Learn:**
- `serde` basics (the "serde book" has all you need in 20 min): `#[derive(Deserialize)]`, field renaming, default values, flattening.
- `jiff` (recommended over `chrono` for new code — better API, same author as `chrono`) for dates, durations, timezones. If jiff feels exotic, `chrono` is fine.
- `thiserror` for defining your error enum, or `anyhow::Result` if you want to skip error-type design entirely for the first pass. Use `anyhow` now, switch to `thiserror` later if you care.

This step is the one where Rust feels nice and where mistakes are cheapest. Spend time here.

## Step 4 — Async polling, decoupled from UI

**Do:**
- Add `tokio = { version = "1", features = ["full"] }`, `reqwest = { features = ["json"] }`.
- Build a `TodoistPoller` as a plain async function: takes a `mpsc::Sender<Vec<Task>>`, loops with `tokio::time::interval(Duration::from_secs(300))`, fetches, parses, sends. No Slint involvement yet.
- Same shape for `WeatherPoller`.
- Test them with a dummy consumer that just prints, no UI.

**Learn:**
- Tokio's official "Tokio Tutorial" — chapters Hello Tokio, Spawning, Channels, Select. Don't try to memorize tokio; you need just these four ideas: `tokio::spawn`, `tokio::select!`, `tokio::time::interval`, `mpsc::channel`.
- `reqwest` is trivial once you've seen one example.
- The mental model: one tokio runtime on a background thread, N poller tasks on it, each sends updates through a channel. The UI thread owns the event loop — it never awaits anything.

This is the step where a first Rust project typically stalls. Budget accordingly.

## Step 5 — Bridging tokio → Slint main thread

**Do:**
- Spawn the tokio runtime on a dedicated thread (`std::thread::spawn` + `tokio::runtime::Builder::new_multi_thread()`). Pass a `Weak<MainWindow>` (Slint's weak handle) into the pollers.
- When a poller has new data, call `slint::invoke_from_event_loop(move || { if let Some(w) = weak.upgrade() { w.set_tasks(...) } })`. This is the bridge.
- Sketch it once on a toy screen (just an updating `Text`) before wiring real widgets.

**Learn:**
- Slint docs page "Running in a Thread" / `invoke_from_event_loop` / `Weak`. This is the single most important page of Slint docs for this project — read it twice.
- Why: Slint objects are not `Send` — you cannot hold a `MainWindow` across await points. The `Weak<T>` handle *is* `Send`, and `invoke_from_event_loop` queues a closure onto the UI thread. That's the whole trick.

## Step 6 — Dynamic data into the UI: the Model trait

**Do:**
- Feed `Vec<Task>` into Slint's tasks list. You'll need Slint's `Model`/`ModelRc` (or the simpler `VecModel` for a first pass).
- Replace the calendar grid's hardcoded cells with a `for cell in month-cells` driven from Rust. A `MonthCell` struct with `{day: int, is_today: bool, has_task: bool}` works.
- Replace the clock and weather labels with bound properties, updated on a Slint `Timer` (for the clock) and from poller updates (for weather).

**Learn:**
- Slint `Model` / `ModelRc` / `VecModel` — one docs page.
- Slint `Timer` (main-thread-only) — use for the clock; don't use tokio for per-second UI updates.

## Step 7 — Interaction: tap-to-complete task

**Do:**
- Add a `TouchArea` over each task row, `clicked => { root.ask-close(task.id) }`.
- `ask-close` callback bubbles up to Rust, which opens a Slint `PopupWindow` for confirmation.
- On confirm, send the task-id through an `mpsc::Sender<Command>` into the tokio side, which calls `close_task` via reqwest.
- The next poll picks up the change; don't try to mutate local state optimistically on the first pass.

**Learn:**
- Slint `TouchArea`, `PopupWindow`, callback propagation (child-to-parent via exposed callbacks).
- Command-pattern channel from UI to async side (just another `mpsc`).

## Step 8 — Fonts, icons, Czech locale

**Do:**
- Embed `meteocons-webfont.ttf` via Slint's `import` or `font-family`, same for Roboto. Slint supports embedding fonts at compile time.
- Czech day/month names: hand-roll a `[&str; 12]` / `[&str; 7]` lookup. Don't wire up `fluent` or `gettext` for a personal project — overkill.
- Map OpenWeatherMap icon codes to meteocons glyphs via a static `HashMap` (or a `match`).

**Learn:**
- Slint font embedding docs (one page).

## Step 9 — Backlight control

**Do:**
- Drop `rpi-backlight` entirely. Write to `/sys/class/backlight/*/brightness` directly with `std::fs::write`. Wrap in a struct that hides the path. Stub it out with a no-op on dev machines (check if the sysfs path exists at startup).
- Bind a Slint `Slider` to an `in-out property <float> brightness` with a callback that writes the sysfs file.

**Learn:**
- Nothing specific — this is the easiest step.

## Step 10 — Deploy on the Pi

**Do:**
- Build with the `i-slint-backend-linuxkms` feature for direct DRM/KMS rendering — no X, no compositor. This is the single biggest performance win versus the Kivy version.
- Cross-compile with `cross build --release --target aarch64-unknown-linux-gnu`.
- scp the binary + assets, run as a systemd service (`User=pi`, `Type=simple`, `Restart=always`, proper `After=network-online.target`).
- Put the Pi into kiosk mode: disable desktop autostart, have systemd own the display.

**Learn:**
- Slint's linuxkms backend docs (short).
- `systemctl --user` services or a plain `/etc/systemd/system/kalendar.service`.
- DRM permissions: the running user needs to be in the `video` and `render` groups.

## Step 11 — Polish (optional, as you feel like it)

- `tracing` + `tracing-subscriber` instead of `println!`.
- Config via env vars through `dotenvy` (same shape as the current `.env`).
- Error surface: swap `anyhow` for a real `thiserror` enum at module boundaries once you have a feel for where errors actually propagate.
- A handful of integration tests using `wiremock` for HTTP.

## Dependencies — minimum viable `Cargo.toml`

```
slint = "1"
tokio = { version = "1", features = ["rt-multi-thread", "time", "sync", "macros"] }
reqwest = { version = "0.12", features = ["json", "rustls-tls"], default-features = false }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
jiff = "0.1"           # or chrono = "0.4"
dotenvy = "0.15"
anyhow = "1"
```

Prefer `rustls-tls` over `native-tls` — avoids pulling OpenSSL into your cross-compile, which is a classic first-project trap.

## Things I'd deliberately *not* do on the first pass

- No abstract trait for "task provider" — put Todoist and Birthdays as two functions returning `Vec<Task>`, merge the results. Revisit when you add a third source (you won't).
- No custom error enum until you've written the happy path end-to-end.
- No swipe gestures on the carousel — use buttons or a timer first. Swipes are polish.
- No graph/plot for the forecast — the Python version had it commented out anyway.

---

## Unresolved questions

- 32-bit (armv7) or 64-bit (aarch64) Raspberry Pi OS on the 3A?
- DSI 7" official touchscreen or HDMI screen + USB touch? Changes DRM setup slightly.
- OK to bump polling to Todoist 5 min / weather 10 min, or do you want faster?
- Keep exact Czech wording from `widgets/mainscreen.py` templates, or rework?
- Slint license: personal-use royalty-free is fine — confirm you're OK with GPL/MIT+royalty terms.
- `jiff` (newer, nicer) vs `chrono` (more examples, stabler ecosystem)?
- Cross-compile from your dev machine, or build on a beefier Pi 4/5 if you own one?
- Keep `viewer.py` around in `python/` as historical reference, or delete it?

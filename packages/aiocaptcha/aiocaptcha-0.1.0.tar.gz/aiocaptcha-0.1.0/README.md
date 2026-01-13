# AioCaptcha (aiogram middleware)

Minimal captcha middleware for **aiogram v3**.

Behavior:
- Any user interaction with the bot is **blocked** until the user passes the captcha.
- Captcha is an inline keyboard with emojis. The bot asks the user to click the required emoji.
- Successful users can be stored **persistently** (SQLite) so they never need to pass captcha again.

## Requirements

- Python 3.10+ (recommended)
- `aiogram>=3.0.0`

## Install

```bash
pip install aiocaptcha
```

## Quick start

Create a bot file like [Source/main.py](Source/main.py) and run it.

### 1) Set the token

```bash
export BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
```

### 2) Run

```bash
python Source/main.py
```

## Usage

<details>
<summary><b>Minimal (in-memory)</b></summary>

Users will be considered “verified” only until the bot restarts.

```python
from aiogram import Bot, Dispatcher
from aiocaptcha import CaptchaManager

bot = Bot(token="...")
dp = Dispatcher()

captcha = CaptchaManager()
captcha.setup(dp)

# ... register your handlers
await dp.start_polling(bot)
```

</details>

<details>
<summary><b>Persistent (SQLite)</b></summary>

Users who passed captcha will be stored in `captcha.sqlite3` and won’t be asked again after restarts.

```python
from aiogram import Bot, Dispatcher
from aiocaptcha import CaptchaManager, SqliteCaptchaStorage

bot = Bot(token="...")
dp = Dispatcher()

storage = SqliteCaptchaStorage("captcha.sqlite3")
captcha = CaptchaManager(storage=storage)
captcha.setup(dp)

await dp.start_polling(bot)
```

> Note: `SqliteCaptchaStorage` uses a single connection with a lock and is fine for typical small bots.

</details>

<details>
<summary><b>Custom storage (your own)</b></summary>

You can provide your own storage to persist “verified” users.

The required interface is:

```python
from typing import Protocol


class CaptchaStorage(Protocol):
  def is_verified(self, user_id: int) -> bool: ...

  def mark_verified(self, user_id: int) -> None: ...

  def reset(self, user_id: int) -> None: ...
```

Example: a simple file-backed JSON storage (minimal example):

```python
import json
from pathlib import Path
from typing import Set

from aiocaptcha import CaptchaManager, CaptchaOptions


class JsonCaptchaStorage:
  def __init__(self, path: str = "verified.json") -> None:
    self.path = Path(path)
    self._verified: Set[int] = set()
    self._load()

  def _load(self) -> None:
    if not self.path.exists():
      return
    data = json.loads(self.path.read_text("utf-8"))
    self._verified = set(int(x) for x in data.get("verified", []))

  def _save(self) -> None:
    self.path.write_text(
      json.dumps({"verified": sorted(self._verified)}, ensure_ascii=False),
      "utf-8",
    )

  def is_verified(self, user_id: int) -> bool:
    return user_id in self._verified

  def mark_verified(self, user_id: int) -> None:
    self._verified.add(user_id)
    self._save()

  def reset(self, user_id: int) -> None:
    self._verified.discard(user_id)
    self._save()


opts = CaptchaOptions()
storage = JsonCaptchaStorage("verified.json")
captcha = CaptchaManager(options=opts, storage=storage)
```

For production/multi-instance setups, a Redis-based storage is usually a better fit.

</details>

## Configuration

<details>
<summary><b>CaptchaOptions</b></summary>

Use `CaptchaOptions` to customize messages and emoji pool:

```python
from aiocaptcha import CaptchaManager, CaptchaOptions

opts = CaptchaOptions(
    prompt_text="Please verify you're human by clicking {target}",
    passed_text="Captcha passed successfully! ✅",
    wrong_alert="Incorrect choice. Please try again.",
    pool=("🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼"),
    choices=4,
    ttl_seconds=120,
)

captcha = CaptchaManager(options=opts)
```

### Available options

- `callback_prefix` — prefix for callback data (default: `aiocaptcha`)
- `pool` — tuple of emojis
- `choices` — how many buttons are shown
- `ttl_seconds` — challenge expiration time
- `prompt_text` — message template. Use `{target}`
- `passed_text` — message after passing
- `wrong_alert` — alert text on wrong click

</details>

## How it works

<details>
<summary><b>Implementation notes</b></summary>

- The library attaches:
  - an **update-level middleware** (`dp.update.middleware(...)`) that blocks all updates from non-verified users;
  - a small router that handles captcha callback queries.
- When a non-verified user sends any message/clicks any button, the bot sends (or edits) a captcha message.
- On correct click the user becomes verified; on wrong click the captcha regenerates.

</details>

## Logging

<details>
<summary><b>Events and setup</b></summary>

The library logs events using Python `logging` under the logger name `aiocaptcha`:

- `captcha_passed user_id=...`
- `captcha_failed user_id=... answer=... expected=...`
- `captcha_sent user_id=... chat_id=... message_id=...`

Enable logging in your app:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
```

</details>

## Notes / limitations

<details>
<summary><b>Notes</b></summary>

- Captcha state and verification are keyed by `user_id`.
- In groups, a captcha message is sent to the chat where the interaction happened.
- If you run multiple bot instances, use a shared storage (SQLite on shared disk, or implement your own storage like Redis).

</details>

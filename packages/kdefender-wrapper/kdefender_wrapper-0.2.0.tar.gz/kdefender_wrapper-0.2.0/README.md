# K-Defender-wrapper

🛡️ **K-Defender-wrapper** is an async Python wrapper that integrates Telegram bots
with **K-Defender**, providing centralized message filtering and injection protection.

Designed for **aiogram / Telethon-based bots**.

---

## Features

- Async-safe verdict requests
- Telethon-based backend listener
- Decorator-based protection (`@kdefender_check`)
- Injection detection (via K-Defender)
- Safe-by-default blocking
- Zero business logic coupling

---

## Installation

```bash
pip install kdefender-wrapper
```

## Quick Start
```python
import asyncio
from kdefender_wrapper import setup, kdefender_check

await setup(
    bot=bot,
    api_id=API_ID,
    api_hash=API_HASH,
    session=SESSION,
    group_id=GROUP_ID,
    chat_token=CHAT_TOKEN,
    kdefender_id=K_DEFENDER_ID,
)

@kdefender_check()
async def handler(message):
    await message.answer("✅ Message accepted")
```

## How It Works
1. User message is intercepted
2. Text is sent to K-Defender group
3. JSON verdict is awaited
4. Message is allowed or blocked based on verdict
5. All checks are serialized and timeout-safe.
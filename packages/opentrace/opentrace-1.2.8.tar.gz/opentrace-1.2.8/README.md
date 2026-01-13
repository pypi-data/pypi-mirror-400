# OpenTrace Python SDK

Official Python client for [OpenTrace Analytics](https://github.com/del4pp/opentrace). Built for performance, privacy, and full marketing attribution across Web, Bots, and Backend services.

## Installation

```bash
pip install opentrace
```

## Quick Start (General)

```python
from opentrace import OpenTrace

# Initialize (point to your self-hosted instance)
ot = OpenTrace(
    host="https://analytics.your-domain.com", 
    project_id="ot_web_xxxxx" # Find this in OpenTrace Settings -> Resource UID
)

# Track any event
ot.track_event("server_booted", payload={"version": "1.0.0"})
```

---

## 🌐 Web & E-commerce Integration (Flask, Django, etc.)

For web applications, the SDK allows you to track server-side events (like purchases or cart actions) while maintaining marketing attribution (Facebook CAPI, UTMs).

### 1. Tracking Cart & Conversions
Send events directly from your business logic to ensure 100% accuracy (bypassing ad-blockers).

```python
@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    # ... your logic ...
    
    ot.track_event(
        name="add_to_cart",
        session_id=ot.get_user_hash(user_email_or_ip),
        payload={
            "product_name": "Premium Plan",
            "value": 49.99,
            "currency": "USD"
        }
    )
    return {"status": "success"}

@app.route('/api/checkout/complete', methods=['POST'])
def complete_purchase():
    # Track final conversion with marketing IDs for Meta/TikTok CAPI
    ot.capture(
        name="purchase",
        payload={"amount": 49.99, "transaction_id": "TX_789"},
        user_id=ot.get_user_hash(current_user.id),
        fbclid=request.args.get('fbclid'), # Pass from URL for attribution
        ttclid=request.cookies.get('ttclid')
    )
    return {"status": "paid"}
```

---

## 🤖 Telegram Bot Integration

OpenTrace is uniquely optimized for Telegram. Use it to track deep-links and user behavior.

### Automatic UTM Resolution
When a user starts your bot via a tracking link (e.g., `t.me/bot?start=utm_XXXX`), the SDK can automatically fetch the campaign metadata.

```python
@router.message(Command("start"))
async def start_handler(message: Message, command: CommandObject):
    # Pass the 'start' argument to track_event
    ot.track_event(
        name="bot_start",
        bot_param=command.args, # SDK auto-fetches 'source', 'campaign', etc.
        session_id=str(message.from_user.id)
    )
```

---

## 👤 User Identity & Persistence

To track a user’s journey over time (User Timeline), use a consistent `session_id`. OpenTrace provides a helper to anonymize user data:

```python
# Generate a short anonymous hash (e.g. 'a1b2c3d4e5f6')
# Recommended for Telegram IDs or IP addresses
user_hash = ot.get_user_hash(raw_id)

# Every event sent with this hash will be grouped in the dashboard
ot.track_event("page_visit", session_id=user_hash)
```

---

## 📖 API Reference

### `OpenTrace(host, [project_id], [debug])`
- `host`: The base URL of your OpenTrace installation.
- `project_id`: Default Resource UID.
- `debug`: If `True`, enables detailed logging.

### `.track_event(name, ...)`
The primary method for server-side business events.
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `name` | `str` | **Required**. (e.g., `checkout_step_1`). |
| `session_id`| `str` | Used to group events in the User Timeline. |
| `bot_param` | `str` | Telegram `start` code. Auto-resolves UTMs from DB. |
| `payload` | `dict`| Any custom JSON data (cart items, prices, names). |
| `utm_source`| `str` | Manual UTM Source override. |
| `utm_medium`| `str` | Manual UTM Medium override. |
| `utm_campaign`| `str` | Manual UTM Campaign override. |

### `.capture(name, ...)`
Parity with the JavaScript SDK. Ideal for telemetry and Conversion API (CAPI).
- `fbclid` / `ttclid`: Used for server-side attribution to Facebook/TikTok.
- `user_id`: Maps to `session_id`.
- `meta`: Same as `payload`.

### `.get_user_hash(raw_id)`
Creates a persistent 16-char anonymous hash for a raw ID (like email or TG ID).

---

## ⚡ Technical Features

- **Daemon Environment**: Network requests are non-blocking and happen in background threads. Your app performance is unaffected.
- **Unified Attribution**: Connects Bot clicks, Web visits, and Backend purchases into a single user story.
- **Privacy First**: Designed to work with anonymized identifiers while keeping data accurate.

## License
MIT

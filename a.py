#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==============================================================================
# 🚀 SENZO CHANNEL GROWER BOT v2.0
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Multiple Source Channels → Your Target Channel Auto-Forwarder
# Private Owner-Only Access | Telethon Hybrid (Userbot + Bot)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import asyncio
import json
import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

# ==============================================================================
# 🌐 HEALTH CHECK SERVER (Koyeb / Render er jonno)
# ==============================================================================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"SENZO BOT ACTIVE")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass


def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"✅ Health server running on port {port}")


# ==============================================================================
# ⚙️ CONFIGURATION (Sob env variables theke)
# ==============================================================================

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
SESSION_STRING = os.environ.get("SESSION_STRING", "")

TARGET_CHANNEL = int(os.environ.get("TARGET_CHANNEL", 0))

_sources_env = os.environ.get("SOURCE_CHANNELS", "")
SOURCE_CHANNELS = [int(x.strip()) for x in _sources_env.split(",") if x.strip()]

FORWARD_DELAY = float(os.environ.get("FORWARD_DELAY", 0.5))
COPY_MODE = os.environ.get("COPY_MODE", "false").lower() == "true"
SKIP_KEYWORDS = [k for k in os.environ.get("SKIP_KEYWORDS", "").split(",") if k]

CONFIG_FILE = "grower_config.json"

# ==============================================================================
# VALIDATION
# ==============================================================================
if not API_ID or not API_HASH or not BOT_TOKEN or not OWNER_ID:
    print("❌ Missing required env variables (API_ID, API_HASH, BOT_TOKEN, OWNER_ID)")
    exit(1)

# ==============================================================================
# LOGGING
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("grower.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ==============================================================================
# CONFIG
# ==============================================================================
def load_config():
    default = {
        "active": True,
        "forwarded_count": 0,
        "failed_count": 0,
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return {**default, **json.load(f)}
        except:
            return default
    return default


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)


config = load_config()

# ==============================================================================
# CLIENTS
# ==============================================================================
bot = TelegramClient("senzo_bot_session", API_ID, API_HASH)
user = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


# ==============================================================================
# KEYBOARDS
# ==============================================================================
def main_kb():
    return [
        [Button.inline("📊 Status", b"status"), Button.inline("⚙️ Settings", b"settings")],
        [Button.inline("📥 Sources", b"sources"), Button.inline("📢 Target", b"target")],
        [Button.inline("▶️ Resume" if not config["active"] else "⏸ Pause", b"toggle")],
        [Button.inline("❓ Help", b"help")]
    ]


def is_owner(uid):
    return uid == OWNER_ID


# ==============================================================================
# BOT HANDLERS
# ==============================================================================
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    if not is_owner(event.sender_id):
        await event.respond(
            "🔒 **Access Denied**\n\n"
            "Ei bot private. Shudhu owner use korte parbe.",
            parse_mode="md"
        )
        return

    status = "🟢 ACTIVE" if config["active"] else "🔴 PAUSED"
    await event.respond(
        f"🚀 **SENZO CHANNEL GROWER**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Status: {status}\n"
        f"📥 Sources: `{len(SOURCE_CHANNELS)}`\n"
        f"📢 Target: `{TARGET_CHANNEL}`\n"
        f"📤 Forwarded: `{config['forwarded_count']}`\n"
        f"❌ Failed: `{config['failed_count']}`\n"
        f"━━━━━━━━━━━━━━━━━━━",
        buttons=main_kb(),
        parse_mode="md"
    )


@bot.on(events.CallbackQuery())
async def callback(event):
    if not is_owner(event.sender_id):
        await event.answer("🔒 Access Denied", alert=True)
        return

    data = event.data.decode()

    if data == "status":
        status = "🟢 ACTIVE" if config["active"] else "🔴 PAUSED"
        await event.edit(
            f"📊 **STATUS**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Bot: {status}\n"
            f"Forwarded: `{config['forwarded_count']}`\n"
            f"Failed: `{config['failed_count']}`\n"
            f"Sources: `{len(SOURCE_CHANNELS)}`\n"
            f"Target: `{TARGET_CHANNEL}`\n"
            f"Started: `{config['started_at']}`",
            buttons=[[Button.inline("⬅️ Back", b"back")]],
            parse_mode="md"
        )

    elif data == "settings":
        await event.edit(
            f"⚙️ **SETTINGS**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Delay: `{FORWARD_DELAY}s`\n"
            f"Copy Mode: `{COPY_MODE}`\n"
            f"Skip Keywords: `{len(SKIP_KEYWORDS)}`\n"
            f"Auto-Forward: {'🟢 On' if config['active'] else '🔴 Off'}",
            buttons=[[Button.inline("⬅️ Back", b"back")]],
            parse_mode="md"
        )

    elif data == "sources":
        text = "📥 **SOURCE CHANNELS**\n━━━━━━━━━━━━━━━━━━━\n"
        for i, s in enumerate(SOURCE_CHANNELS, 1):
            text += f"`{i}.` `{s}`\n"
        await event.edit(text, buttons=[[Button.inline("⬅️ Back", b"back")]], parse_mode="md")

    elif data == "target":
        await event.edit(
            f"📢 **TARGET CHANNEL**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"ID: `{TARGET_CHANNEL}`",
            buttons=[[Button.inline("⬅️ Back", b"back")]],
            parse_mode="md"
        )

    elif data == "toggle":
        config["active"] = not config["active"]
        save_config(config)
        status = "🟢 ACTIVE" if config["active"] else "🔴 PAUSED"
        await event.answer(f"Bot {status}", alert=True)
        await event.edit(
            f"🚀 **SENZO CHANNEL GROWER**\n\nStatus: {status}",
            buttons=main_kb(),
            parse_mode="md"
        )

    elif data == "help":
        await event.edit(
            "❓ **HELP**\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "`/start` — Menu\n"
            "`/stats` — Stats\n"
            "`/add_source <id>` — Source add\n"
            "`/remove_source <id>` — Remove",
            buttons=[[Button.inline("⬅️ Back", b"back")]],
            parse_mode="md"
        )

    elif data == "back":
        status = "🟢 ACTIVE" if config["active"] else "🔴 PAUSED"
        await event.edit(
            f"🚀 **Main Menu** — {status}",
            buttons=main_kb(),
            parse_mode="md"
        )

    await event.answer()


# ==============================================================================
# OWNER COMMANDS
# ==============================================================================
@bot.on(events.NewMessage(pattern="/stats"))
async def stats_cmd(event):
    if not is_owner(event.sender_id):
        return
    await event.respond(
        f"📊 **STATS**\n"
        f"Forwarded: `{config['forwarded_count']}`\n"
        f"Failed: `{config['failed_count']}`\n"
        f"Sources: `{len(SOURCE_CHANNELS)}`\n"
        f"Status: {'🟢 Active' if config['active'] else '🔴 Paused'}",
        parse_mode="md"
    )


@bot.on(events.NewMessage(pattern="/add_source"))
async def add_source_cmd(event):
    if not is_owner(event.sender_id):
        return
    try:
        source = int(event.message.text.split(maxsplit=1)[1].strip())
        if source not in SOURCE_CHANNELS:
            SOURCE_CHANNELS.append(source)
            await event.respond(f"✅ Added: `{source}`\n`Restart bot to apply`", parse_mode="md")
        else:
            await event.respond("⚠️ Already exists.", parse_mode="md")
    except:
        await event.respond("❌ Usage: `/add_source -100xxxxxxxxxx`", parse_mode="md")


@bot.on(events.NewMessage(pattern="/remove_source"))
async def remove_source_cmd(event):
    if not is_owner(event.sender_id):
        return
    try:
        source = int(event.message.text.split(maxsplit=1)[1].strip())
        if source in SOURCE_CHANNELS:
            SOURCE_CHANNELS.remove(source)
            await event.respond(f"✅ Removed: `{source}`\n`Restart bot to apply`", parse_mode="md")
        else:
            await event.respond("⚠️ Not found.", parse_mode="md")
    except:
        await event.respond("❌ Usage: `/remove_source -100xxxxxxxxxx`", parse_mode="md")


# ==============================================================================
# 🚀 AUTO-FORWARD ENGINE
# ==============================================================================
@user.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def auto_forward(event):
    if not config["active"]:
        return

    try:
        message = event.message

        if SKIP_KEYWORDS and message.text:
            for kw in SKIP_KEYWORDS:
                if kw.lower() in message.text.lower():
                    log.info(f"Skipped (keyword): {kw}")
                    return

        if COPY_MODE:
            await user.send_message(entity=TARGET_CHANNEL, message=message)
        else:
            await user.forward_messages(entity=TARGET_CHANNEL, messages=message)

        config["forwarded_count"] += 1
        save_config(config)

        try:
            chat = await event.get_chat()
            chat_title = getattr(chat, "title", "Unknown")
        except:
            chat_title = str(event.chat_id)

        log.info(f"✅ Forwarded | From: {chat_title} | Total: {config['forwarded_count']}")
        await asyncio.sleep(FORWARD_DELAY)

    except Exception as e:
        config["failed_count"] += 1
        save_config(config)
        log.error(f"❌ Failed: {e}")
        await asyncio.sleep(1)


# ==============================================================================
# MAIN
# ==============================================================================
async def main():
    start_health_server()

    print("\n" + "=" * 60)
    print("🚀 SENZO CHANNEL GROWER BOT v2.0")
    print("=" * 60)
    print(f"👑 Owner ID : {OWNER_ID}")
    print(f"📢 Target   : {TARGET_CHANNEL}")
    print(f"📥 Sources  : {len(SOURCE_CHANNELS)} channels")
    print("=" * 60)

    await bot.start(bot_token=BOT_TOKEN)
    bot_me = await bot.get_me()
    print(f"✅ Bot: @{bot_me.username}")

    if not SESSION_STRING:
        print("\n⚠️  No SESSION_STRING — local mode (phone + OTP)")
        if not await user.is_user_authorized():
            await user.start()
        else:
            await user.connect()
    else:
        await user.connect()
        if not await user.is_user_authorized():
            print("❌ SESSION_STRING invalid or expired!")
            return

    user_me = await user.get_me()
    print(f"✅ User: {user_me.first_name} ({user_me.id})")

    print(f"\n📢 Target: {TARGET_CHANNEL}")
    print(f"📊 Status: {'🟢 ACTIVE' if config['active'] else '🔴 PAUSED'}")
    print("=" * 60)
    print("🚀 Bot running... ")
    print("=" * 60 + "\n")

    await asyncio.gather(
        bot.run_until_disconnected(),
        user.run_until_disconnected()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped.")

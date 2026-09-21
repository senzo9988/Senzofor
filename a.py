#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==============================================================================
# 🚀 SENZO CHANNEL GROWER BOT v1.0
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Multiple Source Channels → Your Target Channel Auto-Forwarder
# Private Owner-Only Access | Telethon Hybrid (Userbot + Bot)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import asyncio
import json
import os
import logging
from datetime import datetime
from telethon import TelegramClient, events, Button
from telethon.tl.types import Channel, Chat, User

# ==============================================================================
# ⚙️ CONFIGURATION
# ==============================================================================

API_ID = 20565074
API_HASH = "f76913f874805a3f001b7c2976b5552a"
BOT_TOKEN = "8714630132:AAFLJ7X-Mg3pdWj4KlP278IGJxN27eVNhIQ"
OWNER_ID = 7447563409

# 🎯 TARGET — Tomar nijer channel
TARGET_CHANNEL = -1004304592792

# 📥 SOURCE CHANNELS — Jekhane theke message nibe
SOURCE_CHANNELS = [
    -1003750300679,
    -1003821203045,
    -1003729378638,
    -1004310458547,
    -1003760992371,
    -1003553323813,
    -1003471165085,
    -1004310760463,
    # ⬇️⬇️ EMPTY SLOTS — Pore nijei add korte parbe ⬇️⬇️
    # -1000000000000,
    # -1000000000000,
    # -1000000000000,
    # -1000000000000,
    # -1000000000000,
]

# Forward settings
FORWARD_DELAY = 0.5                 # Message er modhye delay (seconds)
SKIP_KEYWORDS = []                  # Ei word thakle skip (e.g. ["ad", "promo"])
COPY_MODE = False                   # True = copy (no forward tag), False = forward tag

# File paths
CONFIG_FILE = "grower_config.json"

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
# CONFIG LOAD/SAVE
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
user = TelegramClient("senzo_user_session", API_ID, API_HASH)


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
        log.warning(f"Unauthorized: {event.sender_id}")
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
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"Source channel theke message auto forward\n"
        f"hocche tomar channel e. Enjoy! 🔥",
        buttons=main_kb(),
        parse_mode="md"
    )


@bot.on(events.CallbackQuery())
async def callback(event):
    if not is_owner(event.sender_id):
        await event.answer("🔒 Access Denied", alert=True)
        return

    data = event.data.decode()

    # ─── STATUS ───
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

    # ─── SETTINGS ───
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

    # ─── SOURCES ───
    elif data == "sources":
        text = "📥 **SOURCE CHANNELS**\n━━━━━━━━━━━━━━━━━━━\n"
        for i, s in enumerate(SOURCE_CHANNELS, 1):
            text += f"`{i}.` `{s}`\n"
        await event.edit(text, buttons=[[Button.inline("⬅️ Back", b"back")]], parse_mode="md")

    # ─── TARGET ───
    elif data == "target":
        await event.edit(
            f"📢 **TARGET CHANNEL**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"ID: `{TARGET_CHANNEL}`",
            buttons=[[Button.inline("⬅️ Back", b"back")]],
            parse_mode="md"
        )

    # ─── TOGGLE ───
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

    # ─── HELP ───
    elif data == "help":
        await event.edit(
            "❓ **HELP**\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "**Commands:**\n"
            "`/start` — Menu\n"
            "`/stats` — Stats\n"
            "`/add_source <id>` — Source add\n"
            "`/remove_source <id>` — Remove\n\n"
            "**Note:**\n"
            "Bot ke target channel e admin banate hobe.",
            buttons=[[Button.inline("⬅️ Back", b"back")]],
            parse_mode="md"
        )

    # ─── BACK ───
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
        f"━━━━━━━━━━━━━━━━━━━\n"
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
# 🚀 AUTO-FORWARD ENGINE (USERBOT)
# ==============================================================================
@user.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def auto_forward(event):
    """Source theke message ashle target e forward kore"""

    if not config["active"]:
        return

    try:
        message = event.message

        # Skip keyword check
        if SKIP_KEYWORDS and message.text:
            for kw in SKIP_KEYWORDS:
                if kw.lower() in message.text.lower():
                    log.info(f"Skipped (keyword): {kw}")
                    return

        # Forward or copy
        if COPY_MODE:
            await user.send_message(entity=TARGET_CHANNEL, message=message)
        else:
            await user.forward_messages(entity=TARGET_CHANNEL, messages=message)

        # Counter
        config["forwarded_count"] += 1
        save_config(config)

        # Log
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
    os.system("cls" if os.name == "nt" else "clear")

    print("\n" + "=" * 60)
    print("🚀 SENZO CHANNEL GROWER BOT v1.0")
    print("=" * 60)
    print(f"👑 Owner ID : {OWNER_ID}")
    print(f"📢 Target   : {TARGET_CHANNEL}")
    print(f"📥 Sources  : {len(SOURCE_CHANNELS)} channels")
    print("=" * 60)

    # Start bot
    await bot.start(bot_token=BOT_TOKEN)
    bot_me = await bot.get_me()
    print(f"✅ Bot: @{bot_me.username}")

    # Start user client
    if not await user.is_user_authorized():
        print("\n⚠️  First time login — phone number + OTP lagbe")
        print("   Format: +8801XXXXXXXXX")
        await user.start()
    else:
        await user.connect()

    user_me = await user.get_me()
    print(f"✅ User: {user_me.first_name} ({user_me.id})")

    print(f"\n📥 Sources:")
    for s in SOURCE_CHANNELS:
        print(f"   • {s}")
    print(f"\n📢 Target: {TARGET_CHANNEL}")
    print(f"📊 Status: {'🟢 ACTIVE' if config['active'] else '🔴 PAUSED'}")
    print(f"📤 Forwarded: {config['forwarded_count']}")
    print("=" * 60)
    print("🚀 Bot running... Ctrl+C to stop")
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
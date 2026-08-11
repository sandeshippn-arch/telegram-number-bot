#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════╗
║   💀 AHMAD BOT - Number Info v2.0 💀                 ║
║   Developer: @buntyxahmad                            ║
║   WhatsApp: @teamlegend1                             ║
╚══════════════════════════════════════════════════════╝
"""

import requests
import json
import os
import time
import logging
from datetime import datetime
from telegram import (
    Bot, InlineKeyboardButton, InlineKeyboardMarkup, 
    Update, MessageEntity
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.error import BadRequest

# ═══════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════

BOT_TOKEN = "8376469890:AAFdqayPS2fT1Rw6KNLhad2PXIBrw6m3Nyw"
ADMIN_ID = 1752541652
OWNER_USERNAME = "@SANDESH870"
OWNER_NAME = "SANDESH SINGH"
API_URL = "https://sim-info-api.wasif-ali.workers.dev/?search={}"

# Database file — Ahmad branded
DB_FILE = "ahmad_bot_database.json"

# ═══════════════════════════════════════════════════════
# DATABASE (JSON-based)
# ═══════════════════════════════════════════════════════

def load_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "channels": ["@SANDESH_VIP_MOD"],
            "message_of_day": "",
            "blocked_users": [],
            "stats": {"total_users": 0, "total_searches": 0},
            "users": {},
            "broadcast_list": []
        }

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

DB = load_db()

# ═══════════════════════════════════════════════════════
# STYLING & FORMATTING
# ═══════════════════════════════════════════════════════

def bold_text(text):
    return f"<b>{text}</b>"

# ═══════════════════════════════════════════════════════
# CHANNEL CHECK
# ═══════════════════════════════════════════════════════

async def get_not_joined_channels(user_id: int) -> list:
    """Get list of channels user hasn't joined"""
    db = load_db()
    channels = db.get("channels", ["@SANDESH_VIP_MOD"])
    not_joined = []
    
    for channel in channels:
        try:
            bot = Bot(token=BOT_TOKEN)
            member = await bot.get_chat_member(
                chat_id=channel, 
                user_id=user_id
            )
            if member.status in ["left", "kicked", "banned"]:
                not_joined.append(channel)
        except Exception as e:
            logging.warning(f"Channel check error for {channel}: {e}")
            not_joined.append(channel)
    
    return not_joined

# ═══════════════════════════════════════════════════════
# VERIFICATION MESSAGE
# ═══════════════════════════════════════════════════════

def verification_message(user_name, not_joined_channels):
    """Generate attractive verification message"""
    db = load_db()
    all_channels = db.get("channels", ["@SANDESH_VIP_MOD"])
    
    channels_status = ""
    for ch in all_channels:
        if ch in not_joined_channels:
            channels_status += f'        ❌ {ch}\n'
        else:
            channels_status += f'        ✅ {ch}\n'
    
    msg = f"""<b>🔒 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃</b>

<b>👋 Hello {user_name}!</b>

<b>⚠️ Please join all required channels to use this bot:</b>

{channels_status}
<b>🔄 After joining all channels, click VERIFY below</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 DEVELOPER: {OWNER_USERNAME}</b>
<b>💬 CHANNEL: @SANDESH_VIP_MOD</b>"""
    
    keyboard = []
    for ch in all_channels:
        keyboard.append([InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch.replace('@', '')}")])
    
    keyboard.append([InlineKeyboardButton("✅ 𝗩𝗘𝗥𝗜𝗙𝗬", callback_data="verify_join")])
    
    return msg, InlineKeyboardMarkup(keyboard)

# ═══════════════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════════════

def main_menu_keyboard():
    """Generate main menu with attractive buttons"""
    keyboard = [
        [
            InlineKeyboardButton("📞 𝗚𝗲𝘁 𝗡𝘂𝗺𝗯𝗲𝗿", callback_data="get_number"),
            InlineKeyboardButton("📊 𝗠𝘆 𝗦𝘁𝗮𝘁𝘀", callback_data="my_stats")
        ],
        [
            InlineKeyboardButton("👤 𝗣𝗿𝗼𝗳𝗶𝗹𝗲", callback_data="profile"),
            InlineKeyboardButton("📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", callback_data="channel")
        ],
        [
            InlineKeyboardButton("💰 𝗗𝗼𝗻𝗮𝘁𝗲 / 𝗣𝗿𝗲𝗺𝗶𝘂𝗺", callback_data="donate"),
            InlineKeyboardButton("👥 𝗧𝗲𝗮𝗺", callback_data="team")
        ],
        [
            InlineKeyboardButton("📡 𝗟𝗶𝘃𝗲 𝗧𝗿𝗮𝗳𝗳𝗶𝗰", callback_data="live_traffic"),
            InlineKeyboardButton("⚙️ 𝗠𝗼𝗿𝗲", callback_data="more_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def welcome_message(user_name, user_id):
    """Generate attractive welcome/start message — AHMAD branding"""
    db = load_db()
    total_users = db.get("stats", {}).get("total_users", 0)
    
    msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   💀 SANDESH VIP BOT 𝗩𝟮.𝟬 💀       ║</b>
<b>╚══════════════════════════════╝</b>

<b>👋 Welcome, {user_name}!</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>🔰 YOUR USER ID:</b> <code>{user_id}</code>
<b>📊 TOTAL USERS:</b> <b>{total_users}</b>

<b>🔥 This bot provides:</b>
<b>📞</b> Number Information
<b>🔍</b> CNIC Details
<b>📍</b> Address Lookup
<b>📡</b> Network Provider
<b>⚡</b> Fast & Reliable Results

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>👇 Tap a button below to start</b>

<b>💀 Dev: {OWNER_USERNAME}</b>
<b>📢 Channel: @SANDESH_VIP_MOD</b>"""
    
    return msg

# ═══════════════════════════════════════════════════════
# NUMBER INFO RESULT
# ═══════════════════════════════════════════════════════

def format_number_info(record):
    """Format number info in attractive hacker style"""
    name = record.get("name", "Unknown")
    mobile = record.get("mobile", "Unknown")
    cnic = record.get("cnic", "Unknown")
    address = record.get("address", "Unknown")
    network = record.get("network", "Unknown")
    
    # Determine network emoji
    network_emoji = "📡"
    if "Jazz" in str(network):
        network_emoji = "🟡"
    elif "Telenor" in str(network):
        network_emoji = "🟢"
    elif "Zong" in str(network):
        network_emoji = "🔴"
    elif "Ufone" in str(network):
        network_emoji = "🔵"
    elif "SCO" in str(network) or "Special" in str(network):
        network_emoji = "⚪"
    
    msg = f"""<b>╔════════════════════════════════╗</b>
<b>║   💀 𝗥𝗘𝗦𝗨𝗟𝗧 𝗗𝗘𝗧𝗔𝗜𝗟𝗦 💀          ║</b>
<b>╚════════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

<b>👤 𝗡𝗔𝗠𝗘:</b>
   <b>{name}</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

<b>📞 𝗡𝗨𝗠𝗕𝗘𝗥:</b>
   <code>{mobile}</code>

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

<b>🪪 𝗖𝗡𝗜𝗖:</b>
   <code>{cnic}</code>

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

<b>📍 𝗔𝗗𝗗𝗥𝗘𝗦𝗦:</b>
   <b>{address}</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

<b>{network_emoji} 𝗡𝗘𝗧𝗪𝗢𝗥𝗞:</b>
   <b>{network}</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

<b>⚡ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬: 𝗔𝗛𝗠𝗔𝗗 𝗕𝗢𝗧</b>
<b>💀 Developer: {OWNER_USERNAME}</b>
<b>📢 Channel: @SANDESH_VIP_MOD</b>"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 𝗦𝗲𝗮𝗿𝗰𝗵 𝗔𝗴𝗮𝗶𝗻", callback_data="get_number")],
        [
            InlineKeyboardButton("📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url="https://t.me/SANDESH_VIP_MOD"),
            InlineKeyboardButton("👤 𝗗𝗲𝘃", url="https://t.me/SANDESH_VIP_MOD")
        ]
    ]
    
    return msg, InlineKeyboardMarkup(keyboard)

# ═══════════════════════════════════════════════════════
# SUB MENUS
# ═══════════════════════════════════════════════════════

def more_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🆘 𝗛𝗲𝗹𝗽", callback_data="help")],
        [InlineKeyboardButton("📋 𝗣𝗿𝗶𝘃𝗮𝗰𝘆 𝗣𝗼𝗹𝗶𝗰𝘆", callback_data="privacy")],
        [InlineKeyboardButton("📜 𝗧𝗲𝗿𝗺𝘀 𝗼𝗳 𝗨𝘀𝗲", callback_data="terms")],
        [InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ═══════════════════════════════════════════════════════
# ADMIN COMMANDS
# ═══════════════════════════════════════════════════════

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel for managing bot"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗! Admin only!")
        return
    
    db = load_db()
    channels = db.get("channels", [])
    total_users = db.get("stats", {}).get("total_users", 0)
    total_searches = db.get("stats", {}).get("total_searches", 0)
    
    keyboard = [
        [InlineKeyboardButton("➕ 𝗔𝗱𝗱 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", callback_data="admin_add_channel")],
        [InlineKeyboardButton("🗑 𝗥𝗲𝗺𝗼𝘃𝗲 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", callback_data="admin_remove_channel")],
        [InlineKeyboardButton("📋 𝗩𝗶𝗲𝘄 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀", callback_data="admin_view_channels")],
        [InlineKeyboardButton("📢 𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👥 𝗕𝗹𝗼𝗰𝗸 𝗨𝘀𝗲𝗿", callback_data="admin_block")],
        [InlineKeyboardButton("📊 𝗦𝘁𝗮𝘁𝘀", callback_data="admin_stats")],
        [InlineKeyboardButton("📝 𝗦𝗲𝘁 𝗠𝗢𝗧𝗗", callback_data="admin_set_motd")],
        [InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="back_to_main")]
    ]
    
    msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   ⚙️ 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟 ⚙️          ║</b>
<b>╚══════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>👤 Admin:</b> <code>{update.effective_user.id}</code>
<b>👥 Total Users:</b> <b>{total_users}</b>
<b>🔍 Total Searches:</b> <b>{total_searches}</b>
<b>📢 Channels:</b> <b>{len(channels)}</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>⚙️ Select an option below:</b>"""
    
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command with parameter"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗!")
        return
    
    if not context.args:
        await update.message.reply_text(
            f"""<b>⚙️ 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>📢 /admin addchannel @channel</b>
<b>🗑 /admin removechannel @channel</b>
<b>📋 /admin listchannels</b>
<b>📡 /admin broadcast &lt;message&gt;</b>
<b>🚫 /admin blockuser &lt;user_id&gt;</b>
<b>✅ /admin unblockuser &lt;user_id&gt;</b>
<b>📊 /admin botstats</b>
<b>📝 /admin setmotd &lt;message&gt;</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 Dev: {OWNER_USERNAME}</b>""",
            parse_mode='HTML'
        )
        return
    
    command = context.args[0]
    
    if command == "addchannel":
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /admin addchannel @channel")
            return
        channel = context.args[1]
        db = load_db()
        channels = db.get("channels", [])
        if channel not in channels:
            channels.append(channel)
            db["channels"] = channels
            save_db(db)
            await update.message.reply_text(f"✅ Channel <b>{channel}</b> added!", parse_mode='HTML')
        else:
            await update.message.reply_text(f"⚠️ Channel <b>{channel}</b> already exists!", parse_mode='HTML')
    
    elif command == "removechannel":
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /admin removechannel @channel")
            return
        channel = context.args[1]
        db = load_db()
        channels = db.get("channels", [])
        if channel in channels:
            channels.remove(channel)
            db["channels"] = channels
            save_db(db)
            await update.message.reply_text(f"✅ Channel <b>{channel}</b> removed!", parse_mode='HTML')
        else:
            await update.message.reply_text(f"⚠️ Channel <b>{channel}</b> not found!", parse_mode='HTML')
    
    elif command == "listchannels":
        db = load_db()
        channels = db.get("channels", [])
        if channels:
            ch_list = "\n".join([f"  📢 <b>{ch}</b>" for ch in channels])
            await update.message.reply_text(f"<b>📋 REQUIRED CHANNELS:</b>\n{ch_list}", parse_mode='HTML')
        else:
            await update.message.reply_text("⚠️ No channels set!")
    
    elif command == "blockuser":
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /admin blockuser <user_id>")
            return
        user_id = int(context.args[1])
        db = load_db()
        blocked = db.get("blocked_users", [])
        if user_id not in blocked:
            blocked.append(user_id)
            db["blocked_users"] = blocked
            save_db(db)
            await update.message.reply_text(f"✅ User <b>{user_id}</b> blocked!", parse_mode='HTML')
        else:
            await update.message.reply_text(f"⚠️ User already blocked!")
    
    elif command == "unblockuser":
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /admin unblockuser <user_id>")
            return
        user_id = int(context.args[1])
        db = load_db()
        blocked = db.get("blocked_users", [])
        if user_id in blocked:
            blocked.remove(user_id)
            db["blocked_users"] = blocked
            save_db(db)
            await update.message.reply_text(f"✅ User <b>{user_id}</b> unblocked!", parse_mode='HTML')
        else:
            await update.message.reply_text(f"⚠️ User not in block list!")
    
    elif command == "botstats":
        db = load_db()
        stats = db.get("stats", {})
        msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗦 📊            ║</b>
<b>╚══════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>👥 Total Users:</b> <b>{stats.get('total_users', 0)}</b>
<b>🔍 Total Searches:</b> <b>{stats.get('total_searches', 0)}</b>
<b>🚫 Blocked Users:</b> <b>{len(db.get('blocked_users', []))}</b>
<b>📢 Channels:</b> <b>{len(db.get('channels', []))}</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 Dev: {OWNER_USERNAME}</b>"""
        await update.message.reply_text(msg, parse_mode='HTML')
    
    elif command == "broadcast":
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /admin broadcast <message>")
            return
        message_text = " ".join(context.args[1:])
        db = load_db()
        users = db.get("users", {})
        sent = 0
        failed = 0
        for uid in users.keys():
            try:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=f"📢 <b>BROADCAST:</b>\n\n{message_text}",
                    parse_mode='HTML'
                )
                sent += 1
            except:
                failed += 1
        
        await update.message.reply_text(
            f"✅ Broadcast sent!\n"
            f"<b>Sent:</b> {sent}\n"
            f"<b>Failed:</b> {failed}",
            parse_mode='HTML'
        )
    
    elif command == "setmotd":
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /admin setmotd <message>")
            return
        motd = " ".join(context.args[1:])
        db = load_db()
        db["message_of_day"] = motd
        save_db(db)
        await update.message.reply_text(f"✅ Message of the day set!", parse_mode='HTML')
    
    else:
        await update.message.reply_text(f"❌ Unknown admin command: {command}")

# ═══════════════════════════════════════════════════════
# CALLBACK HANDLERS
# ═══════════════════════════════════════════════════════

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all inline button callbacks"""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user_name = query.from_user.first_name or "User"
    
    # Block check
    db = load_db()
    if user_id in db.get("blocked_users", []):
        await query.edit_message_text("🚫 𝗬𝗢𝗨 𝗔𝗥𝗘 𝗕𝗟𝗢𝗖𝗞𝗘𝗗! Contact admin.", parse_mode='HTML')
        return
    
    # Admin callbacks
    if data.startswith("admin_"):
        await handle_admin_callback(query, context, data, user_id)
        return
    
    # Verify join
    if data == "verify_join":
        not_joined = await get_not_joined_channels(user_id)
        if not_joined:
            msg, keyboard = verification_message(user_name, not_joined)
            await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)
        else:
            msg = welcome_message(user_name, user_id)
            await query.edit_message_text(msg, parse_mode='HTML', reply_markup=main_menu_keyboard())
            db = load_db()
            if str(user_id) not in db.get("users", {}):
                db.setdefault("users", {})[str(user_id)] = {
                    "name": user_name,
                    "joined": datetime.now().isoformat(),
                    "searches": 0
                }
                db["stats"]["total_users"] = db["stats"]["total_users"] + 1
                save_db(db)
        return
    
    # Channel check before any action
    not_joined = await get_not_joined_channels(user_id)
    if not_joined:
        msg, keyboard = verification_message(user_name, not_joined)
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)
        return
    
    # Main menu actions
    if data == "get_number":
        await query.edit_message_text(
            f"<b>📞 𝗘𝗡𝗧𝗘𝗥 𝗡𝗨𝗠𝗕𝗘𝗥</b>\n\n"
            f"<b>Send the phone number to search:</b>\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"<b>💡 Example:</b> <code>03249560618</code>\n\n"
            f"<b>🔙 Use /start to go back</b>",
            parse_mode='HTML'
        )
        context.user_data["waiting_for_number"] = True
        return
    
    elif data == "my_stats":
        db = load_db()
        user_data = db.get("users", {}).get(str(user_id), {})
        searches = user_data.get("searches", 0)
        joined = user_data.get("joined", "Unknown")
        
        msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   📊 𝗠𝗬 𝗦𝗧𝗔𝗧𝗦 📊            ║</b>
<b>╚══════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>👤 𝗡𝗔𝗠𝗘:</b> <b>{user_name}</b>
<b>🆔 𝗨𝗦𝗘𝗥 𝗜𝗗:</b> <code>{user_id}</code>
<b>🔍 𝗦𝗘𝗔𝗥𝗖𝗛𝗘𝗦:</b> <b>{searches}</b>
<b>📅 𝗝𝗢𝗜𝗡𝗘𝗗:</b> <b>{joined[:10] if joined != "Unknown" else "Unknown"}</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 Dev: {OWNER_USERNAME}</b>"""
        
        keyboard = [[InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="back_to_main")]]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif data == "profile":
        msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   👤 𝗨𝗦𝗘𝗥 𝗣𝗥𝗢𝗙𝗜𝗟𝗘 👤         ║</b>
<b>╚══════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>👤 𝗡𝗔𝗠𝗘:</b> <b>{user_name}</b>
<b>🆔 𝗨𝗦𝗘𝗥 𝗜𝗗:</b> <code>{user_id}</code>
<b>👤 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘:</b> @{query.from_user.username or "Not set"}

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 Dev: {OWNER_USERNAME}</b>"""
        
        keyboard = [[InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="back_to_main")]]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif data == "channel":
        msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   📢 𝗢𝗨𝗥 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 📢           ║</b>
<b>╚══════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>📢 Join our official channel:</b>

<b>👇 @teamlegend1 👇</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 Dev: {OWNER_USERNAME}</b>"""
        
        keyboard = [
            [InlineKeyboardButton("📢 @SANDESH_VIP_MOD", url="https://t.me/SANDESH_VIP_MOD")],
            [InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="back_to_main")]
        ]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif data == "donate":
        msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   💰 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 𝗨𝗦 💰           ║</b>
<b>╚══════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💚 If you love this bot, support us!</b>

<b>📢 Join our channel for updates:</b>
<b>👉 @teamlegend1</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 Dev: {OWNER_USERNAME}</b>"""
        
        keyboard = [
            [InlineKeyboardButton("📢 @SANDESH_VIP_MOD", url="https://t.me/SANDESH_VIP_MOD")],
            [InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="back_to_main")]
        ]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif data == "team":
        msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   👥 𝗢𝗨𝗥 𝗧𝗘𝗔𝗠 👥             ║</b>
<b>╚══════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 𝗗𝗘𝗩𝗘𝗟𝗢𝗣𝗘𝗥:</b>
   <b>{OWNER_USERNAME}</b>

<b>📢 𝗖𝗛𝗔𝗡𝗡𝗘𝗟:</b>
   <b>@SANDESH_VIP_MOD</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>⚡ Powered by {OWNER_NAME} Bot v2.0</b>"""
        
        keyboard = [
            [InlineKeyboardButton("👤 Dev", url="https://t.me/SANDESH_VIP_MOD")],
            [InlineKeyboardButton("📢 Channel", url="https://t.me/SANDESH_VIP_MOD")],
            [InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="back_to_main")]
        ]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif data == "live_traffic":
        db = load_db()
        total_users = db.get("stats", {}).get("total_users", 0)
        total_searches = db.get("stats", {}).get("total_searches", 0)
        
        msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   📡 𝗟𝗜𝗩𝗘 𝗧𝗥𝗔𝗙𝗙𝗜𝗖 📡         ║</b>
<b>╚══════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>👥 Active Users:</b> <b>{total_users}</b>
<b>🔍 Total Searches:</b> <b>{total_searches}</b>
<b>📊 Bot Uptime:</b> <b>Online ✅</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>⚡ Real-time monitoring active</b>
<b>💀 Dev: {OWNER_USERNAME}</b>"""
        
        keyboard = [[InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="back_to_main")]]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif data == "more_menu":
        await query.edit_message_text(
            f"<b>⚙️ 𝗠𝗢𝗥𝗘 𝗢𝗣𝗧𝗜𝗢𝗡𝗦</b>",
            parse_mode='HTML',
            reply_markup=more_menu_keyboard()
        )
        return
    
    elif data == "back_to_main":
        msg = welcome_message(user_name, user_id)
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=main_menu_keyboard())
        return
    
    elif data == "help":
        msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   🆘 𝗛𝗘𝗟𝗣 𝗚𝗨𝗜𝗗𝗘 🆘          ║</b>
<b>╚══════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>📞 /start</b> - Start the bot
<b>🔍 Send number</b> - Search info
<b>📢 Join channel</b> - Required

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 Dev: {OWNER_USERNAME}</b>"""
        
        keyboard = [[InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="more_menu")]]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif data == "privacy":
        msg = f"""<b>📋 𝗣𝗥𝗜𝗩𝗔𝗖𝗬 𝗣𝗢𝗟𝗜𝗖𝗬</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>• We don't store your data</b>
<b>• Your searches are private</b>
<b>• No data sharing with 3rd parties</b>
<b>• All info is from public databases</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 Dev: {OWNER_USERNAME}</b>"""
        
        keyboard = [[InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="more_menu")]]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif data == "terms":
        msg = f"""<b>📜 𝗧𝗘𝗥𝗠𝗦 𝗢𝗙 𝗨𝗦𝗘</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>• This bot is for educational purposes</b>
<b>• Don't misuse the information</b>
<b>• We're not responsible for misuse</b>
<b>• Join our channel for updates</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 Dev: {OWNER_USERNAME}</b>"""
        
        keyboard = [[InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="more_menu")]]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif data == "checker_set":
        msg = f"""<b>🛡 𝗖𝗛𝗘𝗖𝗞𝗘𝗥 𝗦𝗘𝗧</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>⚡ Coming Soon!</b>
<b>🔧 Under development</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>📢 Join @SANDESH_VIP_MOD for updates</b>"""
        
        keyboard = [[InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="back_to_main")]]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    else:
        await query.answer("Unknown button!", show_alert=True)

async def handle_admin_callback(query, context, data, user_id):
    """Handle admin panel callbacks"""
    if user_id != ADMIN_ID:
        await query.edit_message_text("❌ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗!", parse_mode='HTML')
        return
    
    if data == "admin_stats":
        db = load_db()
        stats = db.get("stats", {})
        msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗦 📊            ║</b>
<b>╚══════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>👥 Total Users:</b> <b>{stats.get('total_users', 0)}</b>
<b>🔍 Total Searches:</b> <b>{stats.get('total_searches', 0)}</b>
<b>🚫 Blocked:</b> <b>{len(db.get('blocked_users', []))}</b>
<b>📢 Channels:</b> <b>{len(db.get('channels', []))}</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 Dev: {OWNER_USERNAME}</b>"""
        
        keyboard = [[InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="admin_panel")]]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "admin_view_channels":
        db = load_db()
        channels = db.get("channels", [])
        if channels:
            ch_list = "\n".join([f"  📢 <b>{ch}</b>" for ch in channels])
            msg = f"<b>📋 REQUIRED CHANNELS:</b>\n\n{ch_list}"
        else:
            msg = "⚠️ No channels set!"
        
        keyboard = [[InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="admin_panel")]]
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "admin_add_channel":
        await query.edit_message_text(
            f"<b>➕ 𝗔𝗗𝗗 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</b>\n\n"
            f"<b>Send channel username (e.g., @channel):</b>",
            parse_mode='HTML'
        )
        context.user_data["admin_action"] = "add_channel"
    
    elif data == "admin_remove_channel":
        db = load_db()
        channels = db.get("channels", [])
        if not channels:
            await query.edit_message_text("⚠️ No channels to remove!", parse_mode='HTML')
            return
        
        keyboard = []
        for ch in channels:
            keyboard.append([InlineKeyboardButton(f"🗑 {ch}", callback_data=f"remove_ch_{ch}")])
        keyboard.append([InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸", callback_data="admin_panel")])
        
        await query.edit_message_text(
            f"<b>🗑 𝗥𝗘𝗠𝗢𝗩𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</b>\n\n<b>Select a channel to remove:</b>",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith("remove_ch_"):
        channel = data.replace("remove_ch_", "")
        db = load_db()
        channels = db.get("channels", [])
        if channel in channels:
            channels.remove(channel)
            db["channels"] = channels
            save_db(db)
            await query.edit_message_text(f"✅ Channel <b>{channel}</b> removed!", parse_mode='HTML')
        else:
            await query.edit_message_text(f"⚠️ Channel not found!", parse_mode='HTML')
    
    elif data == "admin_broadcast":
        await query.edit_message_text(
            f"<b>📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧</b>\n\n"
            f"<b>Send the message to broadcast:</b>",
            parse_mode='HTML'
        )
        context.user_data["admin_action"] = "broadcast"
    
    elif data == "admin_block":
        await query.edit_message_text(
            f"<b>🚫 𝗕𝗟𝗢𝗖𝗞 𝗨𝗦𝗘𝗥</b>\n\n"
            f"<b>Send user ID to block:</b>",
            parse_mode='HTML'
        )
        context.user_data["admin_action"] = "block_user"
    
    elif data == "admin_set_motd":
        await query.edit_message_text(
            f"<b>📝 𝗦𝗘𝗧 𝗠𝗢𝗧𝗗</b>\n\n"
            f"<b>Send message of the day:</b>",
            parse_mode='HTML'
        )
        context.user_data["admin_action"] = "set_motd"
    
    elif data == "admin_panel":
        await admin_panel_inline(query, context)
    
    else:
        await query.answer("Unknown admin action!", show_alert=True)

async def admin_panel_inline(query, context):
    """Show admin panel inline"""
    db = load_db()
    total_users = db.get("stats", {}).get("total_users", 0)
    total_searches = db.get("stats", {}).get("total_searches", 0)
    channels = db.get("channels", [])
    
    keyboard = [
        [InlineKeyboardButton("➕ 𝗔𝗱𝗱 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", callback_data="admin_add_channel")],
        [InlineKeyboardButton("🗑 𝗥𝗲𝗺𝗼𝘃𝗲 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", callback_data="admin_remove_channel")],
        [InlineKeyboardButton("📋 𝗩𝗶𝗲𝘄 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀", callback_data="admin_view_channels")],
        [InlineKeyboardButton("📢 𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🚫 𝗕𝗹𝗼𝗰𝗸 𝗨𝘀𝗲𝗿", callback_data="admin_block")],
        [InlineKeyboardButton("📊 𝗦𝘁𝗮𝘁𝘀", callback_data="admin_stats")],
        [InlineKeyboardButton("📝 𝗦𝗲𝘁 𝗠𝗢𝗧𝗗", callback_data="admin_set_motd")],
        [InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸 𝘁𝗼 𝗠𝗮𝗶𝗻", callback_data="back_to_main")]
    ]
    
    msg = f"""<b>╔══════════════════════════════╗</b>
<b>║   ⚙️ 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟 ⚙️          ║</b>
<b>╚══════════════════════════════╝</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>👥 Total Users:</b> <b>{total_users}</b>
<b>🔍 Total Searches:</b> <b>{total_searches}</b>
<b>📢 Channels:</b> <b>{len(channels)}</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>⚙️ Select an option:</b>"""
    
    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# ═══════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    # Block check
    db = load_db()
    if user_id in db.get("blocked_users", []):
        await update.message.reply_text("🚫 𝗬𝗢𝗨 𝗔𝗥𝗘 𝗕𝗟𝗢𝗖𝗞𝗘𝗗! Contact admin @SANDESH870")
        return
    
    # Update user in DB
    db = load_db()
    if str(user_id) not in db.get("users", {}):
        db.setdefault("users", {})[str(user_id)] = {
            "name": user_name,
            "joined": datetime.now().isoformat(),
            "searches": 0
        }
        db["stats"]["total_users"] = db["stats"]["total_users"] + 1
        save_db(db)
    
    # Check channel membership
    not_joined = await get_not_joined_channels(user_id)
    if not_joined:
        msg, keyboard = verification_message(user_name, not_joined)
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
    else:
        msg = welcome_message(user_name, user_id)
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=main_menu_keyboard())
    
    # Show MOTD if set
    motd = db.get("message_of_day", "")
    if motd:
        await update.message.reply_text(f"<b>📢 𝗠𝗢𝗧𝗗:</b> {motd}", parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    msg = f"""<b>🆘 𝗛𝗘𝗟𝗣 & 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>/start</b> - Start the bot
<b>/help</b> - Show help
<b>/menu</b> - Show menu
<b>/stats</b> - Your stats

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>📞 Send any number to search info</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>💀 Dev: {OWNER_USERNAME}</b>
<b>📢 Channel: @SANDESH_VIP_MOD</b>"""
    
    await update.message.reply_text(msg, parse_mode='HTML')

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /menu command"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    # Check channels
    not_joined = await get_not_joined_channels(user_id)
    if not_joined:
        msg, keyboard = verification_message(user_name, not_joined)
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
        return
    
    msg = welcome_message(user_name, user_id)
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=main_menu_keyboard())

# ═══════════════════════════════════════════════════════
# MESSAGE HANDLER (Number Search & Admin Actions)
# ═══════════════════════════════════════════════════════

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    # Admin actions
    admin_action = context.user_data.get("admin_action")
    if admin_action and user_id == ADMIN_ID:
        text = update.message.text or ""
        
        if admin_action == "add_channel":
            if text.startswith("@"):
                db = load_db()
                channels = db.get("channels", [])
                if text not in channels:
                    channels.append(text)
                    db["channels"] = channels
                    save_db(db)
                    await update.message.reply_text(f"✅ Channel <b>{text}</b> added successfully!", parse_mode='HTML')
                else:
                    await update.message.reply_text(f"⚠️ Channel <b>{text}</b> already exists!", parse_mode='HTML')
            else:
                await update.message.reply_text("❌ Please send a valid channel username (e.g., @channel)")
                return
            context.user_data.pop("admin_action", None)
            return
        
        elif admin_action == "broadcast":
            db = load_db()
            users = db.get("users", {})
            sent = 0
            failed = 0
            for uid in users.keys():
                try:
                    await context.bot.send_message(
                        chat_id=int(uid),
                        text=f"📢 <b>BROADCAST:</b>\n\n{text}",
                        parse_mode='HTML'
                    )
                    sent += 1
                    time.sleep(0.05)
                except:
                    failed += 1
            
            await update.message.reply_text(
                f"✅ 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗦𝗘𝗡𝗧!\n\n"
                f"<b>Sent:</b> {sent}\n"
                f"<b>Failed:</b> {failed}",
                parse_mode='HTML'
            )
            context.user_data.pop("admin_action", None)
            return
        
        elif admin_action == "block_user":
            try:
                block_uid = int(text)
                db = load_db()
                blocked = db.get("blocked_users", [])
                if block_uid not in blocked:
                    blocked.append(block_uid)
                    db["blocked_users"] = blocked
                    save_db(db)
                    await update.message.reply_text(f"✅ User <b>{block_uid}</b> blocked!", parse_mode='HTML')
                else:
                    await update.message.reply_text(f"⚠️ User already blocked!", parse_mode='HTML')
            except ValueError:
                await update.message.reply_text("❌ Please send a valid user ID!")
            context.user_data.pop("admin_action", None)
            return
        
        elif admin_action == "set_motd":
            db = load_db()
            db["message_of_day"] = text
            save_db(db)
            await update.message.reply_text(f"✅ Message of the day set!", parse_mode='HTML')
            context.user_data.pop("admin_action", None)
            return
    
    # Check if waiting for number
    if context.user_data.get("waiting_for_number"):
        text = update.message.text or ""
        
        # Basic validation
        if not text.replace(" ", "").replace("-", "").isdigit() and not text.startswith("+"):
            await update.message.reply_text(
                "❌ <b>Invalid number!</b>\n\n"
                "<b>Please send a valid phone number.</b>\n"
                "<b>Example:</b> <code>03249560618</code>",
                parse_mode='HTML'
            )
            return
        
        # Clean number
        number = text.replace(" ", "").replace("-", "").replace("+92", "0")
        if not number.startswith("0"):
            number = "0" + number
        
        # Show loading
        loading_msg = await update.message.reply_text(
            "⏳ <b>Searching...</b>\n"
            "<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            "<b>🔍 Looking up number info...</b>",
            parse_mode='HTML'
        )
        
        try:
            # API call
            api_url = API_URL.format(number)
            response = requests.get(api_url, timeout=15)
            data = response.json()
            
            if data.get("success") and data.get("records"):
                record = data["records"][0]
                result_msg, keyboard = format_number_info(record)
                
                # Update search count
                db = load_db()
                if str(user_id) in db.get("users", {}):
                    db["users"][str(user_id)]["searches"] = db["users"][str(user_id)].get("searches", 0) + 1
                db["stats"]["total_searches"] = db["stats"].get("total_searches", 0) + 1
                save_db(db)
                
                await loading_msg.delete()
                await update.message.reply_text(result_msg, parse_mode='HTML', reply_markup=keyboard)
            else:
                await loading_msg.delete()
                await update.message.reply_text(
                    "❌ <b>NO DATA FOUND!</b>\n\n"
                    "<b>The number you searched is not in our database.</b>\n\n"
                    "<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                    "<b>💡 Try another number</b>\n"
                    "<b>📢 Join: @SANDESH_VIP_MOD</b>",
                    parse_mode='HTML'
                )
        except requests.exceptions.Timeout:
            await loading_msg.delete()
            await update.message.reply_text(
                "⏱ <b>TIMEOUT!</b>\n\n"
                "<b>The API request timed out. Please try again.</b>",
                parse_mode='HTML'
            )
        except Exception as e:
            await loading_msg.delete()
            await update.message.reply_text(
                "❌ <b>ERROR!</b>\n\n"
                "<b>Something went wrong. Please try again.</b>\n\n"
                f"<b>Error:</b> <code>{str(e)[:50]}</code>",
                parse_mode='HTML'
            )
        
        context.user_data.pop("waiting_for_number", None)
        return
    
    # Default: show main menu or check channels
    not_joined = await get_not_joined_channels(user_id)
    if not_joined:
        msg, keyboard = verification_message(user_name, not_joined)
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
    else:
        msg = welcome_message(user_name, user_id)
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=main_menu_keyboard())

# ═══════════════════════════════════════════════════════
# MAIN BOT RUNNER
# ═══════════════════════════════════════════════════════

def main():
    """Start the bot"""
    # Logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("""
╔══════════════════════════════════════════════════════╗
║                                                      ║
║    💀 SANDESH VIP BOT 𝗩𝟮.𝟬 💀                             ║
║    Number Info Telegram Bot                         ║
║                                                      ║
║    Developer: @SANDESH870                    ║
║    Channel: @SANDESH_VIP_MOD                            ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("admin", admin_command))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handler (text only)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("🚀 Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

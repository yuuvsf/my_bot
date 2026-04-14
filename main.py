import asyncio
import random
from telethon import TelegramClient, events, functions, types
from telethon.tl.types import Chat, Channel

# --- SOZLAMALAR ---
api_id = 30778871
api_hash = 'fb1986f77b10a9dc95c43e30120249d3'

client = TelegramClient('session_name', api_id, api_hash)

# Global o'zgaruvchilar
afk_mod = False
afk_reason = ""
tag_running = False 

# .utag uchun tasodifiy gaplar
RANDOM_TEXTS = [
    "Qayerdasiz? 👀", "Guruhga bir kiring! ✨", "Sizni hamma kutyapti... 🔥",
    "Yaxshimisiz? 🌟", "Tezroq kiring, qiziq bo'lyapti! 🚀", "Nega jimsiz? 🤔",
    "Sizsiz zerikarli-ku! ✨", "Bir kelib keting! 👋", "Hamma shu yerda, siz yo'q... ⚡",
    "Tinchlikmi? 🌈", "Sizga bitta gap bor edi... 🙊", "Uxlab qoldingizmi? 😴"
]

# ==========================================
# 1-GURUH: TAGERLAR (.tagall, .utag, .stoptag)
# ==========================================

@client.on(events.NewMessage(pattern=r'\.tagall ?(.*)', outgoing=True))
async def mass_tager(event):
    global tag_running
    tag_running = True
    prefix = event.pattern_match.group(1)
    await event.delete()
    users = [u async for u in client.iter_participants(event.chat_id) if not u.bot and not u.deleted]
    random.shuffle(users)
    for user in users:
        if not tag_running: break
        tag = f"@{user.username}" if user.username else f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        await client.send_message(event.chat_id, f"{prefix} {tag}" if prefix else tag, parse_mode="html")
        await asyncio.sleep(1.2)
    tag_running = False

@client.on(events.NewMessage(pattern=r'\.utag', outgoing=True))
async def universal_tager(event):
    global tag_running
    tag_running = True
    await event.delete()
    users = [u async for u in client.iter_participants(event.chat_id) if not u.bot and not u.deleted]
    random.shuffle(users)
    for user in users:
        if not tag_running: break
        extra = random.choice(RANDOM_TEXTS)
        tag = f"@{user.username}" if user.username else f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        await client.send_message(event.chat_id, f"{tag} {extra}", parse_mode="html")
        await asyncio.sleep(1.2)
    tag_running = False

@client.on(events.NewMessage(pattern=r'\.stoptag', outgoing=True))
async def stop_tag(event):
    global tag_running
    tag_running = False
    await event.edit("🛑 **Taglash to'xtatildi!**"); await asyncio.sleep(2); await event.delete()

# ==========================================
# 2-GURUH: TOZALASH (.purge, .clear)
# ==========================================

@client.on(events.NewMessage(pattern=r'\.purge', outgoing=True))
async def purge_past(event):
    if event.is_reply:
        rep = await event.get_reply_message()
        msgs = [m async for m in client.iter_messages(event.chat_id, max_id=rep.id + 1, from_user='me')]
        await client.delete_messages(event.chat_id, msgs)
    await event.delete()

@client.on(events.NewMessage(pattern=r'\.clear', outgoing=True))
async def clear_future(event):
    if event.is_reply:
        rep = await event.get_reply_message()
        msgs = [m async for m in client.iter_messages(event.chat_id, min_id=rep.id - 1, from_user='me')]
        await client.delete_messages(event.chat_id, msgs)

# ==========================================
# 3-GURUH: FOYDALI (.pin, .unpin, .afk, .calc, .info, .id)
# ==========================================

@client.on(events.NewMessage(pattern=r'\.pin', outgoing=True))
async def pin_cmd(event):
    if event.is_reply: await client.pin_message(event.chat_id, await event.get_reply_message())
    await event.delete()

@client.on(events.NewMessage(pattern=r'\.unpin', outgoing=True))
async def unpin_cmd(event):
    if event.is_reply:
        r = await event.get_reply_message()
        await client(functions.messages.UpdatePinnedMessageRequest(peer=event.chat_id, id=r.id, unpin=True))
    else: await client.unpin_message(event.chat_id)
    await event.delete()

@client.on(events.NewMessage(pattern=r'\.afk (.*)', outgoing=True))
async def set_afk(event):
    global afk_mod, afk_reason
    afk_mod = True; afk_reason = event.pattern_match.group(1) or "Bandman."; await event.delete()

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    if afk_mod and event.is_private: await event.reply(f"🤖 **Avto-javob:** {afk_reason}")

@client.on(events.NewMessage(outgoing=True))
async def off_afk(event):
    global afk_mod
    if afk_mod and ".afk" not in event.text:
        afk_mod = False; m = await event.respond("✅ **Men qaytdim!**"); await asyncio.sleep(2); await m.delete()

@client.on(events.NewMessage(pattern=r'\.calc (.+)', outgoing=True))
async def calc_cmd(event):
    try: await event.edit(f"📊 **Natija:** `{eval(event.pattern_match.group(1))}`")
    except: await event.edit("Xato!")

@client.on(events.NewMessage(pattern=r'\.info', outgoing=True))
async def info_cmd(event):
    target = await event.get_reply_message() if event.is_reply else await event.get_chat()
    u = await client.get_entity(target.from_id if event.is_reply else target)
    await event.edit(f"👤 **Ism:** {u.first_name}\n🆔 **ID:** `{u.id}`\n🏷 **User:** @{u.username}")

@client.on(events.NewMessage(pattern=r'\.id', outgoing=True))
async def id_cmd(event): await event.edit(f"📍 **Chat ID:** `{event.chat_id}`")

# ==========================================
# 4-GURUH: QIZIQARLI (.anim, .type, .hide, .bold, .reverse, .react)
# ==========================================

@client.on(events.NewMessage(pattern=r'\.type (.+)', outgoing=True))
async def type_cmd(event):
    txt = event.pattern_match.group(1); t = ""
    for c in txt: t += c; await event.edit(t + "▒"); await asyncio.sleep(0.1)
    await event.edit(t)

@client.on(events.NewMessage(pattern=r'\.anim (.+)', outgoing=True))
async def anim_cmd(event):
    txt = event.pattern_match.group(1); t = ""
    for c in txt: t += c; await event.edit(t + " ⚡"); await asyncio.sleep(0.2)
    await event.edit(t)

@client.on(events.NewMessage(pattern=r'\.react (.+)', outgoing=True))
async def react_cmd(event):
    if event.is_reply:
        r = await event.get_reply_message()
        await client(functions.messages.SendReactionRequest(peer=event.chat_id, msg_id=r.id, reaction=[types.ReactionEmoji(emoticon=event.pattern_match.group(1))]))
    await event.delete()

@client.on(events.NewMessage(pattern=r'\.reverse', outgoing=True))
async def rev_cmd(event):
    if event.is_reply: r = await event.get_reply_message(); await event.edit(r.text[::-1])

@client.on(events.NewMessage(pattern=r'\.bold (.+)', outgoing=True))
async def bold_cmd(event): await event.edit(f"**{event.pattern_match.group(1)}**")

@client.on(events.NewMessage(pattern=r'\.hide (.+)', outgoing=True))
async def hide_cmd(event): await event.edit(f"||{event.pattern_match.group(1)}||")

# --- ISHGA TUSHIRISH ---
print("🚀 Hamma funksiyalar va Universal Tager tayyor!")
with client:
    client.run_until_disconnected()
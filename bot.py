import time
import re
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- কনফিগারেশন ---
BOT_TOKEN = "8860724639:AAElAgG0Bp08paukQPsO08-GRgb6YqDxZ8w"
GEMINI_API_KEY = "AQ.Ab8RN6LIpIAxy2jDFMh9EUZiexwebg8BylBMp5DfLLErFIgEBA"
OFFICIAL_CHANNEL = "@MrTripleR_YT0"
OFFICIAL_GROUP = "@MrTripleR_YT0"
BOT_VERSION = "v5.1.0 Pro"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

db_groups = {}
verified_users = set()

DEFAULT_SETTINGS = {
    "link_protection": True,
    "bad_word_protection": True,
    "warning_system": True,
    "welcome": True,
    "spam_protection": True,
    "bot_protection": True,
    "auto_reaction": True,
    "ai_assistant": True,
}

# বাংলা ও বাংলিশ গালি ফিল্টার লিস্ট
DEFAULT_BAD_WORDS = [
    "bal", "chuda", "madarchod", "bhenchod", "gunda", "sala", "shala", 
    "magi", "magir", "chod", "voot", "bokachoda", "baler", "chudir", 
    "gud", "putki", "harami", "suor", "suorer", "khanki", "kiros", 
    "balerchagol", "bahenchod", "bastard"
]

# প্রিমিয়াম ইমোজি লিস্ট অটো রিঅ্যাকশনের জন্য
PREMIUM_EMOJIS = ["❤️", "🔥", "✨", "👍", "💯", "🥰", "😎", "🙌", "🤍"]

def create_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'})
    return session

session = create_session()

def get_main_keyboard():
    return {
        "keyboard": [
            [{"text": "🏠 𝐇𝐎𝐌𝐄"}, {"text": "⚙️ 𝐌𝐘 𝐆𝐑𝐎𝐔𝐏𝐒"}],
            [{"text": "📊 𝐒𝐓𝐀𝐓𝐔𝐒"}, {"text": "📖 𝐑𝐔𝐋𝐄𝐒"}],
            [{"text": "🆘 𝐇𝐄𝐋𝐏 & 𝐒𝐔𝐏𝐏𝐎𝐑𝐓"}, {"text": "➕ 𝐀𝐃𝐃 𝐓𝐎 𝐆𝐑𝐎𝐔𝐏"}],
            [{"text": "📋 𝐀𝐂𝐓𝐈𝐕𝐈𝐓𝐘 𝐋𝐎𝐆"}, {"text": "📢 𝐓𝐘𝐍𝐄𝐗 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋"}]
        ],
        "resize_keyboard": True
    }

def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        response = session.post(BASE_URL + "sendMessage", json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Send Error: {e}")

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="Markdown"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        session.post(BASE_URL + "editMessageText", json=payload, timeout=10)
    except:
        pass

def delete_message(chat_id, message_id):
    try:
        session.post(BASE_URL + "deleteMessage", json={"chat_id": chat_id, "message_id": message_id}, timeout=10)
    except:
        pass

def restrict_user(chat_id, user_id, duration_hours=1):
    until_date = int(time.time()) + (duration_hours * 3600)
    payload = {
        "chat_id": chat_id,
        "user_id": user_id,
        "permissions": {"can_send_messages": False},
        "until_date": until_date
    }
    try:
        session.post(BASE_URL + "restrictChatMember", json=payload, timeout=10)
    except:
        pass

def set_message_reaction(chat_id, message_id):
    try:
        emoji = random.choice(PREMIUM_EMOJIS)
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": [{"type": "emoji", "emoji": emoji}]
        }
        session.post(BASE_URL + "setMessageReaction", json=payload, timeout=10)
    except:
        pass

def is_user_admin(chat_id, user_id):
    if chat_id in db_groups and user_id in db_groups[chat_id].get("allowed_admins", set()):
        return True
    try:
        res = session.get(BASE_URL + f"getChatMember?chat_id={chat_id}&user_id={user_id}", timeout=10).json()
        if res.get("ok"):
            status = res["result"]["status"]
            return status in ["administrator", "creator"]
    except:
        pass
    return False

def get_group_administrators(chat_id):
    admin_usernames = set()
    admin_user_ids = set()
    if chat_id in db_groups:
        admin_user_ids.update(db_groups[chat_id].get("allowed_admins", set()))
    try:
        res = session.get(BASE_URL + f"getChatAdministrators?chat_id={chat_id}", timeout=10).json()
        if res.get("ok"):
            for member in res["result"]:
                uid = member.get("user", {}).get("id")
                uname = member.get("user", {}).get("username")
                if uid:
                    admin_user_ids.add(uid)
                if uname:
                    admin_usernames.add(uname.lower())
    except:
        pass
    return admin_user_ids, admin_usernames

def get_chat_title(chat_id):
    try:
        res = session.get(BASE_URL + f"getChat?chat_id={chat_id}", timeout=10).json()
        if res.get("ok"):
            return res["result"].get("title", "Community Chat")
    except:
        pass
    return "Community Chat"

def check_force_join(user_id):
    if user_id in verified_users:
        return True
    try:
        res = session.get(BASE_URL + f"getChatMember?chat_id={OFFICIAL_CHANNEL}&user_id={user_id}", timeout=10).json()
        if res.get("ok"):
            status = res["result"]["status"]
            if status in ["member", "administrator", "creator"]:
                verified_users.add(user_id)
                return True
    except:
        pass
    return False

def main():
    print("⚡ TYNEX Official Bot System Started Successfully...")
    offset = None
    waiting_for_uid = {}

    while True:
        try:
            url = BASE_URL + "getUpdates?timeout=30"
            if offset:
                url += f"&offset={offset}"
            
            response = session.get(url, timeout=40)
            data = response.json()
            
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1

                    if "message" in update:
                        msg = update["message"]
                        chat = msg["chat"]
                        chat_id = chat["id"]
                        chat_type = chat["type"]
                        user = msg.get("from", {})
                        user_id = user.get("id")
                        text = msg.get("text", "") or msg.get("caption", "")
                        user_first_name = user.get("first_name", "User")
                        user_mention = f"[{user_first_name}](tg://user?id={user_id})" if user_id else user_first_name

                        if chat_type in ["group", "supergroup", "channel"]:
                            db_groups.setdefault(chat_id, {
                                "settings": DEFAULT_SETTINGS.copy(),
                                "warnings": {},
                                "allowed_admins": set(),
                                "stats": {"links": 0, "bad_words": 0, "warnings": 0, "restrictions": 0, "bots": 0, "spam": 0, "reactions": 0}
                            })

                        # ১. প্রাইভেট চ্যাট সিস্টেম
                        if chat_type == "private":
                            if not text:
                                continue
                            
                            if user_id in waiting_for_uid:
                                target_gid = waiting_for_uid.pop(user_id)
                                clean_text = text.strip()
                                
                                if clean_text.isdigit():
                                    target_uid = int(clean_text)
                                    if target_gid in db_groups:
                                        db_groups[target_gid]["allowed_admins"].add(target_uid)
                                        send_message(chat_id, f"✅ সফলভাবে ইউজার আইডি `{target_uid}` কে এই গ্রুপের এলাউড এডমিন লিস্টে যুক্ত করা হয়েছে!", reply_markup=get_main_keyboard())
                                    else:
                                        send_message(chat_id, "⚠️ গ্রুপটি ডাটাবেজে পাওয়া যায়নি।", reply_markup=get_main_keyboard())
                                else:
                                    send_message(chat_id, "❌ ভুল ইউআইডি! দয়া করে সঠিক সংখ্যাসূচক আইডি দিন।", reply_markup=get_main_keyboard())
                                continue

                            if text.startswith("/start"):
                                if not check_force_join(user_id):
                                    inline_kb = {
                                        "inline_keyboard": [
                                            [{"text": "📢 𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", "url": f"https://t.me/{OFFICIAL_CHANNEL.lstrip('@')}"}],
                                            [{"text": "✅ 𝐕𝐄𝐑𝐈𝐅𝐘 𝐉𝐎𝐈𝐍", "callback_data": "verify_join"}]
                                        ]
                                    }
                                    send_message(chat_id, f"𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐨𝐮𝐫 𝐨𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 {OFFICIAL_CHANNEL} 𝐟𝐢𝐫𝐬𝐭.", reply_markup=inline_kb)
                                    continue
                                
                                welcome_text = (
                                    "🖤 **TYNEX OFFICIAL**\n\n"
                                    "✨ **PRIVATE BOT ASSISTANT DASHBOARD** ✨\n\n"
                                    "স্বাগতম ভাই! নিচে কিবোর্ড থেকে অপশন সিলেক্ট করুন।"
                                )
                                send_message(chat_id, welcome_text, reply_markup=get_main_keyboard())

                            elif text == "🏠 𝐇𝐎𝐌𝐄":
                                home_text = (
                                    "🏠 **হোম ড্যাশবোর্ড**\n\n"
                                    "🖤 *ব্র্যান্ড:* TYNEX Official\n"
                                    "🚀 *স্ট্যাটাস:* অনলাইন এবং ফুললি একটিভ\n"
                                    f"👥 *সংযুক্ত গ্রুপ:* {len(db_groups)}"
                                )
                                send_message(chat_id, home_text, reply_markup=get_main_keyboard())

                            elif text == "⚙️ 𝐌𝐘 𝐆𝐑𝐎𝐔𝐏𝐒":
                                if not db_groups:
                                    send_message(chat_id, "⚠️ কোনো গ্রুপে বট এড করা নেই! প্রথমে গ্রুপে বট এড করুন।", reply_markup=get_main_keyboard())
                                    continue
                                
                                inline_kb = {"inline_keyboard": [[{"text": f"Group ID: {gid}", "callback_data": f"cfg_grp_{gid}"}] for gid in db_groups]}
                                send_message(chat_id, "⚙️ **ম্যানেজ করার জন্য আপনার গ্রুপটি সিলেক্ট করুন:**", reply_markup=inline_kb)

                            elif text == "📊 𝐒𝐓𝐀𝐓𝐔𝐒":
                                status_text = (
                                    "📊 **বট সিস্টেম স্ট্যাটাস**\n\n"
                                    "🟢 *সার্ভার:* রানিং ও স্টেবল\n"
                                    f"👥 *টোটাল গ্রুপ:* {len(db_groups)}\n"
                                    f"📌 *ভার্সন:* {BOT_VERSION}"
                                )
                                send_message(chat_id, status_text, reply_markup=get_main_keyboard())

                            elif text == "📖 𝐑𝐔𝐋𝐄𝐒":
                                rules_text = (
                                    "📖 **বট ব্যবহারের নিয়মাবলী**\n\n"
                                    "১. গ্রুপে অপ্রয়োজনীয় লিংক বা স্প্যাম করা নিষেধ।\n"
                                    "২. কোনো রকম গালিগালাজ বা অকথ্য ভাষা ব্যবহার করা যাবে না।"
                                )
                                send_message(chat_id, rules_text, reply_markup=get_main_keyboard())

                            elif text == "🆘 𝐇𝐄𝐋𝐏 & 𝐒𝐔𝐏𝐏𝐎𝐑𝐓":
                                help_kb = {
                                    "inline_keyboard": [
                                        [{"text": "🚀 ১. Termux Full Base Setup", "callback_data": "t_setup1"}],
                                        [{"text": "📦 ২. Python & Pip Update", "callback_data": "t_setup2"}],
                                        [{"text": "🛠️ ৩. Common Python Libraries", "callback_data": "t_setup3"}],
                                        [{"text": "📂 ৪. Requirements & Run Bot", "callback_data": "t_setup4"}],
                                        [{"text": "⚙️ ৫. Background & Log Commands", "callback_data": "t_setup5"}],
                                        [{"text": "👨‍💻 সরাসরি সাপোর্ট চ্যানেল", "url": f"https://t.me/{OFFICIAL_CHANNEL.lstrip('@')}"}]
                                    ]
                                }
                                send_message(chat_id, "🆘 **টার্মেক্স ও পাইথন ফুল সেটআপ গাইড সেন্টার:**", reply_markup=help_kb)

                            elif text == "➕ 𝐀𝐃𝐃 𝐓𝐎 𝐆𝐑𝐎𝐔𝐏":
                                bot_info = session.get(BASE_URL + "getMe").json()
                                b_uname = bot_info["result"]["username"] if bot_info.get("ok") else "bot"
                                add_kb = {
                                    "inline_keyboard": [
                                        [{"text": "➕ 𝐛𝐨𝐭‌ টি গ্রুপে এড করুন", "url": f"https://t.me/{b_uname}?startgroup=true"}]
                                    ]
                                }
                                send_message(chat_id, "➕ নিচের বাটনে ক্লিক করে আপনার টেলিগ্রাম গ্রুপে বটটি যুক্ত করে নিন:", reply_markup=add_kb)

                            elif text == "📋 𝐀𝐂𝐓𝐈𝐕𝐈𝐓𝐘 𝐋𝐎𝐆":
                                if not db_groups:
                                    send_message(chat_id, "📋 কোনো অ্যাক্টিভিটি লগ পাওয়া যায়নি।", reply_markup=get_main_keyboard())
                                    continue
                                
                                inline_kb = {"inline_keyboard": [[{"text": f"Log - {gid}", "callback_data": f"log_grp_{gid}"}] for gid in db_groups]}
                                send_message(chat_id, "📋 **মডারেশন স্ট্যাটিস্টিক্স দেখতে গ্রুপ সিলেক্ট করুন:**", reply_markup=inline_kb)

                            elif text == "📢 𝐓𝐘𝐍𝐄𝐗 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋":
                                official_kb = {
                                    "inline_keyboard": [
                                        [{"text": "📢 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", "url": f"https://t.me/{OFFICIAL_CHANNEL.lstrip('@')}"}],
                                        [{"text": "👥 𝐎𝐅𝐅𝐈𝐂𝐈AL 𝐆𝐑𝐎𝐔𝐏", "url": f"https://t.me/{OFFICIAL_GROUP.lstrip('@')}"}]
                                    ]
                                }
                                send_message(chat_id, "📢 **আমাদের অফিসিয়াল কমিউনিটি লিংকসমূহ:**", reply_markup=official_kb)

                            else:
                                send_message(chat_id, "বলো ভাই, কী সাহায্য লাগবে নিচে মেনু থেকে দেখতে পারো।", reply_markup=get_main_keyboard())

                        # ২. গ্রুপ ও চ্যানেল চ্যাট সিস্টেম (মডারেশন ও ওয়েলকাম)
                        elif chat_type in ["group", "supergroup", "channel"]:
                            chat_title = get_chat_title(chat_id)

                            if "new_chat_members" in msg:
                                for member in msg["new_chat_members"]:
                                    if db_groups[chat_id]["settings"].get("welcome", True):
                                        m_name = member.get('first_name', 'User')
                                        welcome_msg = (
                                            f"✨ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 ✨\n\n"
                                            f"𝐇𝐞𝐥𝐥𝐨, {m_name} 👋\n"
                                            f"𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐓𝐨 「{chat_title}」\n\n"
                                            f"🖤 𝐖𝐞'𝐫𝐞 𝐆𝐥𝐚𝐝 𝐓𝐨 𝐇𝐚𝐯𝐞 𝐘𝐨𝐮 𝐇𝐞𝐫𝐞.\n\n"
                                            f"𝐏𝐥𝐞𝐚𝐬𝐞 𝐊𝐞𝐞𝐩 𝐓𝐡𝐞 𝐆𝐫𝐨𝐮𝐩\n"
                                            f"𝐂𝐥𝐞𝐚𝐧 • 𝐅𝐫𝐢𝐞𝐧𝐝𝐥𝐲 • 𝐑𝐞𝐬𝐩𝐞𝐜𝐭𝐟𝐮𝐥\n\n"
                                            f"╰┈➤ 𝐄𝐧𝐣𝐨𝐲 𝐘𝐨𝐮𝐫 𝐓𝐢𝐦𝐞 𝐇𝐞𝐫𝐞 🖤\n\n"
                                            f"— 𝐓𝐘𝐍𝐄𝐗 𝐏𝐫𝐨 𝐀𝐬𝐬𝐢𝐬𝐭𝐚𝐧𝐭"
                                        )
                                        send_message(chat_id, welcome_msg)
                                continue

                            if not user_id:
                                continue

                            settings = db_groups[chat_id]["settings"]
                            stats = db_groups[chat_id]["stats"]
                            violation_detected = False

                            admin_ids, admin_usernames = get_group_administrators(chat_id)
                            is_admin_or_owner = is_user_admin(chat_id, user_id) or (user_id in admin_ids)

                            # লিংক প্রটেকশন (অ্যাডমিন বা ওনারদের মেসেজ ডিলিট হবে না)
                            if not is_admin_or_owner and settings.get("link_protection", True):
                                is_link = re.search(r'https?://|t\.me/|www\.', text, re.IGNORECASE) or "entities" in msg
                                
                                if is_link:
                                    bot_links_found = re.findall(r'(?:t\.me/|@)([a-zA-Z0-9_]{3,32}bot)', text, re.IGNORECASE)
                                    should_delete = True
                                    if bot_links_found:
                                        external_bot_found = False
                                        for b_name in bot_links_found:
                                            if b_name.lower() not in admin_usernames and b_name.lower() != OFFICIAL_CHANNEL.lstrip('@').lower():
                                                external_bot_found = True
                                                break
                                        if not external_bot_found:
                                            should_delete = False
                                    
                                    if should_delete:
                                        violation_detected = True
                                        delete_message(chat_id, msg["message_id"])
                                        stats["links"] += 1
                                        
                                        link_rem_text = (
                                            f"🔗 𝐋𝐈𝐍𝐊 𝐑𝐄𝐌𝐎𝐕𝐄𝐃\n\n"
                                            f"👤 {user_mention}\n\n"
                                            f"𝐔𝐧𝐰𝐚𝐧𝐭𝐞𝐝 𝐋𝐢𝐧𝐤𝐬 𝐀𝐫𝐞 𝐍𝐨𝐭 𝐀𝐥𝐥𝐨𝐰𝐞𝐝 𝐇𝐞𝐫𝐞.\n\n"
                                            f"🗑️ 𝐘𝐨𝐮𝐫 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐑𝐞𝐦𝐨𝐯𝐞𝐝.\n\n"
                                            f"— 𝐓𝐘𝐍𝐄𝐗 𝐏𝐫𝐨 𝐀𝐬𝐬𝐢𝐬𝐭𝐚𝐧𝐭"
                                        )
                                        send_message(chat_id, link_rem_text, parse_mode="Markdown")

                                        # ওয়ার্নিং কাউন্ট ও রেস্ট্রিকশন
                                        warns = db_groups[chat_id]["warnings"]
                                        warns[user_id] = warns.get(user_id, 0) + 1
                                        count = warns[user_id]
                                        stats["warnings"] += 1

                                        if count >= 3:
                                            restrict_user(chat_id, user_id, 1)
                                            stats["restrictions"] += 1
                                            restr_text = (
                                                f"🔒 𝐑𝐄𝐒𝐓𝐑𝐈𝐂𝐓𝐄𝐃\n\n"
                                                f"👤 {user_mention}\n\n"
                                                f"⚠️ 𝐘𝐨𝐮 𝐇𝐚𝐯𝐞 𝐑𝐞𝐚𝐜𝐡𝐞𝐝 𝟑/3 𝐖𝐚𝐫𝐧𝐢𝐧𝐠𝐬.\n\n"
                                                f"🔇 𝐘𝐨𝐮𝐫 𝐌𝐞𝐬𝐬𝐚𝐠𝐢𝐧𝐠 𝐏𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐑𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐞𝐝.\n\n"
                                                f"⏱️ 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧 : 𝟏 𝐇𝐨𝐮𝐫\n\n"
                                                f"— 𝐓𝐘𝐍𝐄𝐗 𝐏𝐫𝐨 𝐀𝐬𝐬𝐢𝐬𝐭𝐚𝐧𝐭"
                                            )
                                            send_message(chat_id, restr_text, parse_mode="Markdown")
                                            warns[user_id] = 0
                                        else:
                                            warn_text = (
                                                f"⚠️ 𝐖𝐀𝐑𝐍𝐈𝐍𝐆\n\n"
                                                f"👤 {user_mention}\n"
                                                f"📌 𝐑𝐞𝐚𝐬𝐨𝐧 : Unwanted Link Sharing\n\n"
                                                f"𝐘𝐨𝐮𝐫 𝐖𝐚𝐫𝐧𝐢𝐧𝐠 : {count}/3\n\n"
                                                f"𝐏𝐥𝐞𝐚𝐬𝐞 𝐅𝐨𝐥𝐥𝐨𝐰 𝐓𝐡𝐞 𝐆𝐫𝐨𝐮𝐩 𝐑𝐮𝐥𝐞𝐬.\n\n"
                                                f"— 𝐓𝐘𝐍𝐄𝐗 𝐏𝐫𝐨 𝐀𝐬𝐬𝐢𝐬𝐭𝐚𝐧𝐭"
                                            )
                                            send_message(chat_id, warn_text, parse_mode="Markdown")
                                        continue

                            # ব্যাড ওয়ার্ড প্রটেকশন (অ্যাডমিন বা ওনারদের মেসেজ ডিলিট হবে না)
                            if not is_admin_or_owner and not violation_detected and settings.get("bad_word_protection", True):
                                clean_text = text.lower()
                                words_in_msg = clean_text.split()
                                is_abusive = False
                                for bw in DEFAULT_BAD_WORDS:
                                    if any(bw in word for word in words_in_msg) or bw in clean_text.replace(" ", ""):
                                        is_abusive = True
                                        break

                                if is_abusive:
                                    violation_detected = True
                                    delete_message(chat_id, msg["message_id"])
                                    stats["bad_words"] += 1
                                    
                                    bad_rem_text = (
                                        f"🚫 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐑𝐄𝐌𝐎𝐕𝐄𝐃\n\n"
                                        f"👤 {user_mention}\n\n"
                                        f"𝐑𝐞𝐚𝐬𝐨𝐧 : 𝐈𝐧𝐚𝐩𝐩𝐫𝐨𝐩𝐫𝐢𝐚𝐭𝐞 𝐋𝐚𝐧𝐠𝐮𝐚𝐠𝐞\n\n"
                                        f"🗑️ 𝐘𝐨𝐮𝐫 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐑𝐞𝐦𝐨𝐯𝐞𝐝.\n\n"
                                        f"𝐏𝐥𝐞𝐚𝐬𝐞 𝐊𝐞𝐞𝐩 𝐓𝐡𝐞 𝐂𝐡𝐚𝐭 𝐑𝐞𝐬𝐩𝐞𝐜𝐭𝐟𝐮𝐥.\n\n"
                                        f"— 𝐓𝐘𝐍𝐄𝐗 𝐏𝐫𝐨 𝐀𝐬𝐬𝐢𝐬𝐭𝐚𝐧𝐭"
                                    )
                                    send_message(chat_id, bad_rem_text, parse_mode="Markdown")
                                    continue

                            # যদি ভায়োলেশন না ঘটে এবং Auto Reaction ON থাকে, তবে সবার মেসেজে রিঅ্যাকশন প্রদান
                            if not violation_detected and settings.get("auto_reaction", True):
                                set_message_reaction(chat_id, msg["message_id"])
                                stats["reactions"] += 1

                    elif "callback_query" in update:
                        cq = update["callback_query"]
                        cq_id = cq["id"]
                        data_val = cq["data"]
                        user_id = cq["from"]["id"]
                        msg_obj = cq.get("message", {})
                        chat_id = msg_obj.get("chat", {}).get("id")
                        msg_id = msg_obj.get("message_id")

                        if data_val == "verify_join":
                            if check_force_join(user_id):
                                session.post(BASE_URL + "answerCallbackQuery", json={"callback_query_id": cq_id, "text": "✅ ভেরিফিকেশন সফল হয়েছে!", "show_alert": True})
                                send_message(user_id, "স্বাগতম! আপনাকে সফলভাবে ভেরিফাই করা হয়েছে।", reply_markup=get_main_keyboard())
                            else:
                                session.post(BASE_URL + "answerCallbackQuery", json={"callback_query_id": cq_id, "text": "❌ আগে আমাদের চ্যানেল জয়েন করুন!", "show_alert": True})

                        elif data_val == "t_setup1":
                            code_text = "🚀 **১. Termux Update & Setup:**\n\n`pkg update -y && pkg upgrade -y && termux-setup-storage`"
                            session.post(BASE_URL + "answerCallbackQuery", json={"callback_query_id": cq_id, "text": "সেটআপ ১ লোড হয়েছে!"})
                            send_message(chat_id, code_text)

                        elif data_val == "t_setup2":
                            code_text = "📦 **২. Python Update:**\n\n`python -m pip install --upgrade pip`"
                            session.post(BASE_URL + "answerCallbackQuery", json={"callback_query_id": cq_id, "text": "সেটআপ ২ লোড হয়েছে!"})
                            send_message(chat_id, code_text)

                        elif data_val == "t_setup3":
                            code_text = "🛠️ **৩. Libraries:**\n\n`pip install requests`"
                            session.post(BASE_URL + "answerCallbackQuery", json={"callback_query_id": cq_id, "text": "সেটআপ ৩ লোড হয়েছে!"})
                            send_message(chat_id, code_text)

                        elif data_val == "t_setup4":
                            code_text = "📂 **৪. Run Bot:**\n\n`python bot.py`"
                            session.post(BASE_URL + "answerCallbackQuery", json={"callback_query_id": cq_id, "text": "সেটআপ ৪ লোড হয়েছে!"})
                            send_message(chat_id, code_text)

                        elif data_val == "t_setup5":
                            code_text = "⚙️ **৫. Background Run:**\n\n`nohup python bot.py > bot.log 2>&1 &`"
                            session.post(BASE_URL + "answerCallbackQuery", json={"callback_query_id": cq_id, "text": "সেটআপ ৫ লোড হয়েছে!"})
                            send_message(chat_id, code_text)

                        elif data_val.startswith("cfg_grp_"):
                            target_chat_id = int(data_val.split("_")[2])
                            session.post(BASE_URL + "answerCallbackQuery", json={"callback_query_id": cq_id, "text": "গ্রুপ প্যানেল লোড হয়েছে!"})
                            
                            panel_text = f"⚙️ **গ্রুপ কন্ট্রোল প্যানেল (ID: `{target_chat_id}`):**"
                            panel_kb = {
                                "inline_keyboard": [
                                    [{"text": "🛠️ সেটিংস টগল মেনু", "callback_data": f"menu_st_{target_chat_id}"}],
                                    [{"text": "➕ এলাউড এডমিন আইডি (UID) যুক্ত করুন", "callback_data": f"add_adm_{target_chat_id}"}],
                                    [{"text": "📋 বর্তমান এলাউড লিস্ট দেখুন", "callback_data": f"list_adm_{target_chat_id}"}]
                                ]
                            }
                            edit_message(chat_id, msg_id, panel_text, reply_markup=panel_kb)

                        elif data_val.startswith("menu_st_"):
                            target_chat_id = int(data_val.split("_")[2])
                            st = db_groups[target_chat_id]["settings"]
                            kb_buttons = []
                            for key, val in st.items():
                                if key == "auto_reaction":
                                    state_str = "🟢 ON" if val else "🔴 OFF"
                                    label = f"✨ Auto Reaction: {state_str}"
                                else:
                                    state_str = "🟢 অন" if val else "🔴 অফ"
                                    label = f"{key.replace('_', ' ').title()}: {state_str}"
                                kb_buttons.append([{"text": label, "callback_data": f"tgl_{target_chat_id}_{key}"}])
                            kb_buttons.append([{"text": "🔙 ফিরে যান", "callback_data": f"cfg_grp_{target_chat_id}"}])
                            edit_message(chat_id, msg_id, f"⚙️ গ্রুপ সেটিংস (`{target_chat_id}`):", reply_markup={"inline_keyboard": kb_buttons})

                        elif data_val.startswith("add_adm_"):
                            target_chat_id = int(data_val.split("_")[2])
                            waiting_for_uid[user_id] = target_chat_id
                            session.post(BASE_URL + "answerCallbackQuery", json={"callback_query_id": cq_id, "text": "দয়া করে চ্যাটে ইউজার আইডি (UID) পাঠান!", "show_alert": True})
                            send_message(chat_id, f"✍️ এই গ্রুপ (`{target_chat_id}`) এর জন্য যে ইউজারের আইডি প্রটেক্ট করতে চান তার **Telegram User ID (UID)** লিখে পাঠান:")

                        elif data_val.startswith("list_adm_"):
                            target_chat_id = int(data_val.split("_")[2])
                            allowed_set = db_groups[target_chat_id].get("allowed_admins", set())
                            if not allowed_set:
                                list_str = "📭 এই গ্রুপে কোনো কাস্টম এলাউড ইউজার আইডি যুক্ত করা নেই।"
                            else:
                                list_str = "👑 **কাস্টম এলাউড ইউজার আইডি সমূহ:**\n"
                                for uid in allowed_set:
                                    list_str += f"• `{uid}`\n"
                            session.post(BASE_URL + "answerCallbackQuery", json={"callback_query_id": cq_id, "text": "লিস্ট লোড হয়েছে!"})
                            send_message(chat_id, list_str)

                        elif data_val.startswith("tgl_"):
                            parts = data_val.split("_")
                            target_chat_id = int(parts[1])
                            setting_key = "_".join(parts[2:])

                            st = db_groups[target_chat_id]["settings"]
                            st[setting_key] = not st[setting_key]

                            kb_buttons = []
                            for key, val in st.items():
                                if key == "auto_reaction":
                                    state_str = "🟢 ON" if val else "🔴 OFF"
                                    label = f"✨ Auto Reaction: {state_str}"
                                else:
                                    state_str = "🟢 অন" if val else "🔴 অফ"
                                    label = f"{key.replace('_', ' ').title()}: {state_str}"
                                kb_buttons.append([{"text": label, "callback_data": f"tgl_{target_chat_id}_{key}"}])
                            kb_buttons.append([{"text": "🔙 ফিরে যান", "callback_data": f"cfg_grp_{target_chat_id}"}])
                            
                            edit_message(chat_id, msg_id, f"⚙️ আপডেটকৃত সেটিংস (`{target_chat_id}`):", reply_markup={"inline_keyboard": kb_buttons})

        except requests.exceptions.RequestException:
            time.sleep(3)
        except Exception as id_err:
            print(f"Error: {id_err}")
            time.sleep(3)

if __name__ == "__main__":
    main()

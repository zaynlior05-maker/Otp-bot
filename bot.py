import os
import logging
import asyncio
import json
import random
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from deep_translator import GoogleTranslator

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch Variables from Railway
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_ID = os.getenv("ADMIN_ID")
GROUP_LOG_ID = os.getenv("GROUP_LOG_ID") 

# Fetch Links from Railway
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "https://t.me/telegram")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/telegram")
RESULTS_LINK = os.getenv("RESULTS_LINK", "https://t.me/telegram")

# Fetch Crypto Wallet Addresses from Railway
LTC_ADDRESS = os.getenv("LTC_ADDRESS", "YOUR_LTC_ADDRESS_NOT_SET")
BTC_ADDRESS = os.getenv("BTC_ADDRESS", "YOUR_BTC_ADDRESS_NOT_SET")
USDT_TRC20_ADDRESS = os.getenv("USDT_TRC20_ADDRESS", "YOUR_USDT_TRC20_ADDRESS_NOT_SET")
USDT_ERC20_ADDRESS = os.getenv("USDT_ERC20_ADDRESS", "YOUR_USDT_ERC20_ADDRESS_NOT_SET")
ETH_ADDRESS = os.getenv("ETH_ADDRESS", "YOUR_ETH_ADDRESS_NOT_SET")
SOL_ADDRESS = os.getenv("SOL_ADDRESS", "YOUR_SOL_ADDRESS_NOT_SET")

# Global Memory Variables
ADMINS = set()
USER_STATES = {}
USER_LANGUAGES = {} 
TEMP_TIER = {} 

# --- PERSISTENT STORAGE PATH ---
# We use the Railway Volume mount path so it never gets deleted on redeploy.
DATA_DIR = "/app/data"
if not os.path.exists(DATA_DIR):
    DATA_DIR = "." # Fallback for local testing
DATA_FILE = os.path.join(DATA_DIR, "bot_data.json")

# Default Subscription Tiers
SUBSCRIPTION_TIERS = [
    {"label": "Daily £15", "val": "15"},
    {"label": "Weekly £30", "val": "30"},
    {"label": "Monthly £50", "val": "50"},
    {"label": "Yearly £100", "val": "100"},
    {"label": "Lifetime £200", "val": "200"}
]

# Fetch all worldwide supported languages
try:
    SUPPORTED_LANGS = GoogleTranslator().get_supported_languages(as_dict=True)
except:
    SUPPORTED_LANGS = {'english': 'en', 'spanish': 'es', 'french': 'fr', 'chinese': 'zh-CN', 'russian': 'ru'}

# Dynamic Text Templates
DYNAMIC_TEXT = {
    "welcome": ("👋 **WELCOME TO UTILITY PANEL**\n➖➖➖➖➖➖➖➖➖➖\n\n🧠 **SYSTEM STATUS**\n├ 🟢 **STATUS:** Operational\n└ 📈 **UPTIME:** 100%\n\n⚡ **WELCOME, {name}**\n🛡️ **PREMIUM UTILITY SOLUTION**\n\n👇 **TO GET STARTED, USE THE MENU BELOW**"),
    "faq": ("❓ **UTILITY PANEL | FAQ**\n➖➖➖➖➖➖➖➖➖➖\n\n❓ **WHAT IS THIS BOT?**\n├ A premium utility solution for managing automated tasks.\n├ Navigate using the control panel below.\n\n➖➖➖➖➖➖➖➖➖➖"),
    "features": ("⚡ **FEATURES**\n➖➖➖➖➖➖➖➖➖➖\n\n🧠 **SYSTEM STATUS**\n├ 🟢 **STATUS:** Operational\n└ 📈 **UPTIME:** 100%\n\n💬 **OUR UTILITY BOT IS PACKED WITH ADVANCED FEATURES!**"),
    "activate": ("💰 **SELECT SUBSCRIPTION PLAN**\n➖➖➖➖➖➖➖➖➖➖\n\n👇 **CHOOSE AMOUNT:**"),
    "dashboard": ("📊 **UTILITY DASHBOARD**\n➖➖➖➖➖➖➖➖➖➖\n\n⛔ **ACCESS DENIED**\n├ 💳 **NO ACTIVE SUBSCRIPTION**\n└ 🛒 **PURCHASE A PLAN TO CONTINUE**\n\n➖➖➖➖➖➖➖➖➖➖"),
    "support": ("💬 **SUPPORT**\n➖➖➖➖➖➖➖➖➖➖\n\n📡 **SUPPORT STATUS**\n├ 🟢 **STATUS:** Active\n└ ⏱️ **RESPONSE:** 2-6h\n\n💬 **COMMON TOPICS**\n├ • PAYMENT PROCESSING\n├ • SUBSCRIPTION ACTIVATION\n├ • BOT SUPPORT\n└ • TECHNICAL ISSUES\n\n➖➖➖➖➖➖➖➖➖➖"),
    "results": ("📈 **RESULTS**\n➖➖➖➖➖➖➖➖➖➖\n\n⭐ **REVIEWS & PERFORMANCE**\n├ • AUTHENTIC USER REVIEWS\n├ • SUCCESS STORIES\n└ • LATEST UPDATES\n\n🌐 **JOIN OUR COMMUNITY**\n👇 **CLICK BELOW**\n\n➖➖➖➖➖➖➖➖➖➖"),
    "commands": ("📋 **COMMANDS**\n🟢 **OPERATIONAL | 📈 UPTIME: 100%**\n➖➖➖➖➖➖➖➖➖➖\n\n🤖 **MAIN COMMANDS**\n◆ 📓 /help\n◆ 💳 /purchase\n◆ ⚙️ /admin")
}

BUTTON_LABELS = {
    "btn_dashboard": "📊 DASHBOARD", "btn_activate": "🔑 ACTIVATE", "btn_features": "⚡ FEATURES",
    "btn_system": "⚙️ SYSTEM", "btn_faq": "❓ FAQ", "btn_results": "📈 RESULTS",
    "btn_commands": "📋 COMMANDS", "btn_profile": "👤 PROFILE", "btn_support": "💬 SUPPORT",
    "btn_language": "🌐 LANGUAGE"
}

# --- Database Loader & Saver ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {"templates": DYNAMIC_TEXT, "labels": BUTTON_LABELS, "tiers": SUBSCRIPTION_TIERS}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"templates": DYNAMIC_TEXT, "labels": BUTTON_LABELS, "tiers": SUBSCRIPTION_TIERS}, f)

# Inject loaded data at startup
data = load_data()
DYNAMIC_TEXT.update(data.get("templates", {}))
BUTTON_LABELS.update(data.get("labels", {}))
SUBSCRIPTION_TIERS = data.get("tiers", SUBSCRIPTION_TIERS)

# --- Format Username Helper ---
def get_user_display(user):
    username = f" (@{user.username})" if user.username else ""
    return f"{user.first_name}{username}"

# --- Translation Engine ---
async def translate_text(text, lang):
    if lang == 'en' or not text: return text
    try: return await asyncio.to_thread(GoogleTranslator(source='auto', target=lang).translate, text)
    except: return text

async def translate_markup(markup, lang):
    if lang == 'en' or not markup: return markup
    if isinstance(markup, InlineKeyboardMarkup):
        new_keyboard = []
        for row in markup.inline_keyboard:
            new_row = []
            for btn in row:
                trans_text = await translate_text(btn.text, lang)
                if btn.url: new_row.append(InlineKeyboardButton(trans_text, url=btn.url))
                else: new_row.append(InlineKeyboardButton(trans_text, callback_data=btn.callback_data))
            new_keyboard.append(new_row)
        return InlineKeyboardMarkup(new_keyboard)
    return markup 

async def safe_send(context, chat_id, text, markup=None, lang='en', edit_message=None):
    trans_text = await translate_text(text, lang)
    trans_markup = await translate_markup(markup, lang)
    trans_text = trans_text.replace("** ", "**").replace(" **", "**")
    
    try:
        if edit_message: await edit_message.edit_text(trans_text, reply_markup=trans_markup, parse_mode="Markdown")
        else: await context.bot.send_message(chat_id=chat_id, text=trans_text, reply_markup=trans_markup, parse_mode="Markdown")
    except Exception as e:
        if edit_message: await edit_message.edit_text(trans_text, reply_markup=trans_markup)
        else: await context.bot.send_message(chat_id=chat_id, text=trans_text, reply_markup=trans_markup)

# --- Notification System ---
async def notify_admin(context: ContextTypes.DEFAULT_TYPE, message: str = None, photo: str = None, caption: str = None):
    targets = []
    if ADMIN_ID: targets.append(ADMIN_ID)
    if GROUP_LOG_ID: targets.append(GROUP_LOG_ID)
    
    for target in targets:
        try:
            if photo: await context.bot.send_photo(chat_id=target, photo=photo, caption=caption, parse_mode="Markdown")
            elif message: await context.bot.send_message(chat_id=target, text=message, parse_mode="Markdown")
        except: pass

# --- Menu Builders ---
def get_back_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])

def get_main_menu():
    keyboard = [
        [KeyboardButton(BUTTON_LABELS["btn_dashboard"])],
        [KeyboardButton(BUTTON_LABELS["btn_activate"]), KeyboardButton(BUTTON_LABELS["btn_features"]), KeyboardButton(BUTTON_LABELS["btn_system"])],
        [KeyboardButton(BUTTON_LABELS["btn_faq"]), KeyboardButton(BUTTON_LABELS["btn_results"]), KeyboardButton(BUTTON_LABELS["btn_commands"])],
        [KeyboardButton(BUTTON_LABELS["btn_profile"]), KeyboardButton(BUTTON_LABELS["btn_support"]), KeyboardButton(BUTTON_LABELS["btn_language"])]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_admin_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Edit Messages", callback_data="admin_templates"), InlineKeyboardButton("🎛️ Edit Main Menus", callback_data="admin_keyboards")], 
        [InlineKeyboardButton("💰 Manage Subscription Tiers", callback_data="admin_tiers")],
        [InlineKeyboardButton("❌ Close Menu", callback_data="admin_logout")]
    ])

def get_admin_tiers_menu():
    keyboard = []
    for i, tier in enumerate(SUBSCRIPTION_TIERS):
        keyboard.append([
            InlineKeyboardButton(f"✏️ {tier['label']}", callback_data=f"edit_tier_label_{i}"),
            InlineKeyboardButton(f"💵 £{tier['val']}", callback_data=f"edit_tier_val_{i}"),
            InlineKeyboardButton("❌ Del", callback_data=f"del_tier_{i}")
        ])
    keyboard.append([InlineKeyboardButton("➕ Add New Tier", callback_data="add_new_tier")])
    keyboard.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")])
    return InlineKeyboardMarkup(keyboard)

def get_admin_templates_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Welcome", callback_data="edit_welcome"), InlineKeyboardButton("FAQ", callback_data="edit_faq")],
        [InlineKeyboardButton("Features", callback_data="edit_features"), InlineKeyboardButton("Activate", callback_data="edit_activate")],
        [InlineKeyboardButton("Dashboard", callback_data="edit_dashboard"), InlineKeyboardButton("Support", callback_data="edit_support")],
        [InlineKeyboardButton("Results", callback_data="edit_results"), InlineKeyboardButton("Commands", callback_data="edit_commands")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_home")]
    ])

def get_admin_keyboards_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Menu: Dashboard", callback_data="kbtn_btn_dashboard"), InlineKeyboardButton("Menu: Activate", callback_data="kbtn_btn_activate")],
        [InlineKeyboardButton("Menu: Features", callback_data="kbtn_btn_features"), InlineKeyboardButton("Menu: System", callback_data="kbtn_btn_system")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_home")]
    ])

def get_tiers_markup():
    keyboard = []
    row = []
    for i, tier in enumerate(SUBSCRIPTION_TIERS):
        row.append(InlineKeyboardButton(tier["label"], callback_data=f"amt_val_{i}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

# --- Core Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    lang = USER_LANGUAGES.get(user.id, 'en')
    welcome_text = DYNAMIC_TEXT["welcome"].replace("{name}", user.first_name)
    USER_STATES[user.id] = None
    
    await safe_send(context, user.id, welcome_text, get_main_menu(), lang)
    activate_markup = InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_LABELS["btn_activate"], callback_data="trigger_payment")]])
    await safe_send(context, user.id, "👇 **QUICK ACTION**", activate_markup, lang)
    
    # Notify Admin with exact @username display
    user_display = get_user_display(user)
    await notify_admin(context, message=f"🟢 **BOT STARTED**\n➖➖➖➖➖➖➖➖➖➖\n👤 **User:** {user_display}\n🆔 **ID:** `{user.id}`\n└ User launched the bot.")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in ADMINS or str(user_id) == str(ADMIN_ID): await show_admin_panel(update, context)
    else:
        USER_STATES[user_id] = "awaiting_admin_password"
        await update.message.reply_text("🔒 **ADMIN AUTHENTICATION**\n\nEnter the admin password to continue:", parse_mode="Markdown")

async def purchase_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang = USER_LANGUAGES.get(user_id, 'en')
    await safe_send(context, user_id, DYNAMIC_TEXT["activate"], get_tiers_markup(), lang)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang = USER_LANGUAGES.get(user_id, 'en')
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("❓ ASK A QUESTION", callback_data="faq_ask")], [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])
    await safe_send(context, user_id, DYNAMIC_TEXT["faq"], markup, lang)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang = USER_LANGUAGES.get(user_id, 'en')
    msg = "❌ **ACCESS DENIED**\n➖➖➖➖➖➖➖➖➖➖\n\nYou need an active subscription to use this command."
    await safe_send(context, user_id, msg, lang=lang)

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = "⚙️ **ADMIN CONTROL PANEL**\n➖➖➖➖➖➖➖➖➖➖\n\nSelect a configuration layer below:"
    markup = get_admin_main_menu()
    if update.message: await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")
    elif update.callback_query: await update.callback_query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

async def handle_menu_clicks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    user_display = get_user_display(user)
    text = update.message.text
    current_state = USER_STATES.get(user_id)
    lang = USER_LANGUAGES.get(user_id, 'en')
    
    if text in BUTTON_LABELS.values():
        await notify_admin(context, message=f"🖱️ **MENU NAVIGATION**\n➖➖➖➖➖➖➖➖➖➖\n👤 **User:** {user_display}\n🆔 **ID:** `{user_id}`\n➡️ **Clicked:** `{text}`")
    
    if current_state == "awaiting_admin_password":
        if text == ADMIN_PASSWORD:
            ADMINS.add(user_id)
            USER_STATES[user_id] = None
            try: await update.message.delete()
            except: pass
            await update.message.reply_text("✅ **Access Granted.**", parse_mode="Markdown")
            await show_admin_panel(update, context)
        else:
            USER_STATES[user_id] = None
            await update.message.reply_text("❌ **Incorrect Password.**", parse_mode="Markdown")
        return
        
    elif current_state == "awaiting_new_tier_label":
        if user_id in ADMINS or str(user_id) == str(ADMIN_ID):
            TEMP_TIER[user_id] = {"label": text}
            USER_STATES[user_id] = "awaiting_new_tier_val"
            await update.message.reply_text("✅ Label saved.\n\nNow, send the numeric **PRICE VALUE** for this tier (e.g. `30`):", parse_mode="Markdown")
        return
        
    elif current_state == "awaiting_new_tier_val":
        if user_id in ADMINS or str(user_id) == str(ADMIN_ID):
            TEMP_TIER[user_id]["val"] = text.strip()
            SUBSCRIPTION_TIERS.append(TEMP_TIER[user_id])
            save_data() # Save permanently
            USER_STATES[user_id] = None
            await update.message.reply_text("✅ **New Tier Added!**", parse_mode="Markdown")
            await update.message.reply_text("⚙️ **TIER EDITOR**", reply_markup=get_admin_tiers_menu(), parse_mode="Markdown")
        return
        
    elif current_state and current_state.startswith("edit_tier_label_"):
        if user_id in ADMINS or str(user_id) == str(ADMIN_ID):
            idx = int(current_state.replace("edit_tier_label_", ""))
            SUBSCRIPTION_TIERS[idx]["label"] = text
            save_data() # Save permanently
            USER_STATES[user_id] = None
            await update.message.reply_text("✅ **Tier Label Updated!**", parse_mode="Markdown")
            await update.message.reply_text("⚙️ **TIER EDITOR**", reply_markup=get_admin_tiers_menu(), parse_mode="Markdown")
        return

    elif current_state and current_state.startswith("edit_tier_val_"):
        if user_id in ADMINS or str(user_id) == str(ADMIN_ID):
            idx = int(current_state.replace("edit_tier_val_", ""))
            SUBSCRIPTION_TIERS[idx]["val"] = text.strip()
            save_data() # Save permanently
            USER_STATES[user_id] = None
            await update.message.reply_text("✅ **Tier Price Updated!**", parse_mode="Markdown")
            await update.message.reply_text("⚙️ **TIER EDITOR**", reply_markup=get_admin_tiers_menu(), parse_mode="Markdown")
        return

    elif current_state == "awaiting_language_input":
        lang_input = text.lower().strip()
        if lang_input in SUPPORTED_LANGS:
            USER_LANGUAGES[user_id] = SUPPORTED_LANGS[lang_input]
            USER_STATES[user_id] = None
            await safe_send(context, user_id, f"✅ Language updated to {lang_input.title()}!", lang=USER_LANGUAGES[user_id])
        elif lang_input in SUPPORTED_LANGS.values():
            USER_LANGUAGES[user_id] = lang_input
            USER_STATES[user_id] = None
            await safe_send(context, user_id, f"✅ Language successfully updated!", lang=USER_LANGUAGES[user_id])
        else:
            await safe_send(context, user_id, "❌ Language not recognized.\nPlease type a valid language name.", get_back_markup(), lang)
        return

    elif current_state and current_state.startswith("awaiting_edit_"):
        if user_id in ADMINS or str(user_id) == str(ADMIN_ID):
            template_key = current_state.replace("awaiting_edit_", "")
            DYNAMIC_TEXT[template_key] = text
            save_data() # Save permanently
            USER_STATES[user_id] = None
            await update.message.reply_text("✅ **Text Template Updated!**", parse_mode="Markdown")
            await update.message.reply_text("⚙️ **TEMPLATE EDITOR**", reply_markup=get_admin_templates_menu(), parse_mode="Markdown")
        return

    elif current_state and current_state.startswith("awaiting_kbtn_"):
        if user_id in ADMINS or str(user_id) == str(ADMIN_ID):
            label_key = current_state.replace("awaiting_kbtn_", "")
            BUTTON_LABELS[label_key] = text
            save_data() # Save permanently
            USER_STATES[user_id] = None
            await update.message.reply_text("✅ **Keyboard saved!**", parse_mode="Markdown")
            await update.message.reply_text("🎛️ **KEYBOARD EDITOR**", reply_markup=get_admin_keyboards_menu(), parse_mode="Markdown")
        return

    elif current_state == "awaiting_faq_question":
        USER_STATES[user_id] = None
        await safe_send(context, user_id, "✅ **TICKET CREATED**\n➖➖➖➖➖➖➖➖➖➖\n\n📌 **TICKET NUMBER:** #5\n⏳ PLEASE WAIT FOR A RESPONSE", lang=lang)
        await notify_admin(context, message=f"❓ **NEW FAQ QUESTION**\n➖➖➖➖➖➖➖➖➖➖\n👤 **From:** {user_display} (`{user_id}`)\n📝 **Question:**\n{text}")
        return

    USER_STATES[user_id] = None

    if text == BUTTON_LABELS["btn_dashboard"]:
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_LABELS["btn_activate"], callback_data="trigger_payment")], [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])
        await safe_send(context, user_id, DYNAMIC_TEXT["dashboard"], markup, lang)
    
    elif text == BUTTON_LABELS["btn_activate"]:
        await safe_send(context, user_id, DYNAMIC_TEXT["activate"], get_tiers_markup(), lang)
    
    elif text == BUTTON_LABELS["btn_features"]:
        await safe_send(context, user_id, DYNAMIC_TEXT["features"], get_back_markup(), lang)
    
    elif text == BUTTON_LABELS["btn_system"]:
        # --- NEW SYSTEM ANIMATION LOGIC ---
        delay_time = random.randint(4, 7)
        
        # Send initial loading message
        initial_msg = f"⚙️ **SYSTEM MENU**\n➖➖➖➖➖➖➖➖➖➖\n\n⏳ **CHECKING SYSTEM...**\n🕚 **TIME:** 1s"
        msg = await context.bot.send_message(chat_id=user_id, text=initial_msg, parse_mode="Markdown")
        
        # Count up loop
        for i in range(2, delay_time + 1):
            await asyncio.sleep(1)
            await msg.edit_text(text=f"⚙️ **SYSTEM MENU**\n➖➖➖➖➖➖➖➖➖➖\n\n⏳ **CHECKING SYSTEM...**\n🕚 **TIME:** {i}s", parse_mode="Markdown")
            
        await asyncio.sleep(1)
        
        # Finally replace it with the true result (translated if necessary)
        final_msg = "⚙️ **SYSTEM STATUS**\n➖➖➖➖➖➖➖➖➖➖\n\n🖥️ **SERVER STATUS**\n├ ✅ **API:** Online\n└ ✅ **SERVICES:** Operational\n\n📊 **PERFORMANCE**\n├ 📶 **UPTIME:** 99.9%\n└ ⚡ **RESPONSE:** < 100ms"
        await safe_send(context, user_id, final_msg, get_back_markup(), lang, edit_message=msg)
    
    elif text == BUTTON_LABELS["btn_results"]:
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"{BUTTON_LABELS['btn_results']} ↗", url=RESULTS_LINK)], [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])
        await safe_send(context, user_id, DYNAMIC_TEXT["results"], markup, lang)
    
    elif text == BUTTON_LABELS["btn_commands"]:
        await safe_send(context, user_id, DYNAMIC_TEXT["commands"], get_back_markup(), lang)
    
    elif text == BUTTON_LABELS["btn_support"]:
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"{BUTTON_LABELS['btn_support']} ↗", url=SUPPORT_LINK), InlineKeyboardButton("📢 CHANNEL ↗", url=CHANNEL_LINK)], [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])
        await safe_send(context, user_id, DYNAMIC_TEXT["support"], markup, lang)
    
    elif text == BUTTON_LABELS["btn_profile"]:
        msg = f"👤 **USER PROFILE**\n➖➖➖➖➖➖➖➖➖➖\n\n🆔 **ACCOUNT DETAILS**\n├ 👤 **ID:** `{user_id}`\n├ 👑 **RANK:** Free Tier\n├ 📅 **DAYS ACTIVE:** 0\n├ 💰 **BALANCE:** £0.00\n└ ⚡ **ACTIONS:** 0\n\n➖➖➖➖➖➖➖➖➖➖"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Deposit", callback_data="trigger_payment")], 
            [InlineKeyboardButton("📜 History", callback_data="view_history")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]
        ])
        await safe_send(context, user_id, msg, markup, lang)
    
    elif text == BUTTON_LABELS["btn_faq"]:
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❓ ASK A QUESTION", callback_data="faq_ask")], [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])
        await safe_send(context, user_id, DYNAMIC_TEXT["faq"], markup, lang)
        
    elif text == BUTTON_LABELS["btn_language"]:
        USER_STATES[user_id] = "awaiting_language_input"
        msg = "🌐 **LANGUAGE SETTINGS**\n➖➖➖➖➖➖➖➖➖➖\n\nPlease type the name of your language below (e.g., Spanish, French, Chinese, Arabic, Hindi, etc.):"
        await safe_send(context, user_id, msg, get_back_markup(), lang)
        
    else:
        msg = "❌ **ACCESS DENIED**\n➖➖➖➖➖➖➖➖➖➖\n\nYou need an active subscription to use this command."
        await safe_send(context, user_id, msg, lang=lang)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    user_display = get_user_display(user)
    current_state = USER_STATES.get(user_id)
    lang = USER_LANGUAGES.get(user_id, 'en')
    
    if current_state == "awaiting_screenshot":
        USER_STATES[user_id] = None
        await safe_send(context, user_id, "✅ **SCREENSHOT RECEIVED**\n➖➖➖➖➖➖➖➖➖➖\n\nYour payment receipt has been successfully submitted to the system.\n⏳ Verification processing window is 15-30 minutes.", lang=lang)
        photo_file_id = update.message.photo[-1].file_id
        await notify_admin(context, photo=photo_file_id, caption=f"📸 **NEW PAYMENT SCREENSHOT**\n👤 **From:** {user_display} (`{user_id}`)\n⚠️ Action required: Verify deposit.")

async def handle_inline_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    user_display = get_user_display(user)
    lang = USER_LANGUAGES.get(user_id, 'en')
    
    if not query.data.startswith("coin_") and query.data != "check_payment":
        await query.answer()

    if query.data == "back_to_main":
        USER_STATES[user_id] = None
        try: await query.message.delete()
        except: pass
        return

    # Admin Routing 
    if query.data == "admin_home" and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        await show_admin_panel(update, context)
    elif query.data == "admin_templates" and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        await query.message.edit_text("⚙️ **TEMPLATE EDITOR**", reply_markup=get_admin_templates_menu(), parse_mode="Markdown")
    elif query.data == "admin_keyboards" and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        await query.message.edit_text("🎛️ **KEYBOARD BUTTON EDITOR**", reply_markup=get_admin_keyboards_menu(), parse_mode="Markdown")
    elif query.data == "admin_tiers" and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        await query.message.edit_text("💰 **TIER CONFIGURATION**\nManage your subscription bases here:", reply_markup=get_admin_tiers_menu(), parse_mode="Markdown")
    elif query.data == "add_new_tier" and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        USER_STATES[user_id] = "awaiting_new_tier_label"
        await query.message.edit_text("➕ **ADD NEW TIER**\n\nSend the **Display Name** for the new tier (e.g. `Weekend Pass £10`):", parse_mode="Markdown")
    elif query.data.startswith("del_tier_") and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        idx = int(query.data.replace("del_tier_", ""))
        SUBSCRIPTION_TIERS.pop(idx)
        save_data() # Save permanently
        await query.message.edit_text("✅ **Tier Deleted.**", reply_markup=get_admin_tiers_menu(), parse_mode="Markdown")
    elif query.data.startswith("edit_tier_label_") and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        idx = query.data.replace("edit_tier_label_", "")
        USER_STATES[user_id] = f"edit_tier_label_{idx}"
        await query.message.edit_text("✏️ Send the new **Display Name** for this tier:", parse_mode="Markdown")
    elif query.data.startswith("edit_tier_val_") and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        idx = query.data.replace("edit_tier_val_", "")
        USER_STATES[user_id] = f"edit_tier_val_{idx}"
        await query.message.edit_text("💵 Send the new **Numeric Price Value** for this tier (e.g. `30`):", parse_mode="Markdown")
    elif query.data.startswith("edit_") and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        template_key = query.data.replace("edit_", "")
        USER_STATES[user_id] = f"awaiting_edit_{template_key}"
        await query.message.edit_text(f"📝 Send the new text body structure for `{template_key.upper()}`:", parse_mode="Markdown")
    elif query.data.startswith("kbtn_") and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        label_key = query.data.replace("kbtn_", "")
        USER_STATES[user_id] = f"awaiting_kbtn_{label_key}"
        await query.message.edit_text(f"🎛️ Send the text you want to label button component `{label_key}` with:", parse_mode="Markdown")
    elif query.data == "admin_logout" and user_id in ADMINS:
        ADMINS.discard(user_id)
        await query.message.edit_text("🚪 **Logged out.**", parse_mode="Markdown")
            
    # User Routing 
    elif query.data == "trigger_payment":
        await safe_send(context, user_id, DYNAMIC_TEXT["activate"], get_tiers_markup(), lang, edit_message=query.message)
        
    elif query.data == "view_history":
        msg = "📜 **TRANSACTION HISTORY**\n➖➖➖➖➖➖➖➖➖➖\n\nNo recent transactions found on this account."
        await safe_send(context, user_id, msg, get_back_markup(), lang, edit_message=query.message)
        
    elif query.data.startswith("amt_val_"):
        idx = int(query.data.replace("amt_val_", ""))
        amount = SUBSCRIPTION_TIERS[idx]["val"]
        msg = "🪙 **SELECT CRYPTO:**"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("LTC", callback_data=f"coin_LTC_{amount}"), InlineKeyboardButton("BTC", callback_data=f"coin_BTC_{amount}")],
            [InlineKeyboardButton("USDT (TRC20)", callback_data=f"coin_USDT-TRC20_{amount}"), InlineKeyboardButton("USDT (ERC20)", callback_data=f"coin_USDT-ERC20_{amount}")],
            [InlineKeyboardButton("ETH", callback_data=f"coin_ETH_{amount}"), InlineKeyboardButton("SOL", callback_data=f"coin_SOL_{amount}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="back_to_main")]
        ])
        await safe_send(context, user_id, msg, markup, lang, edit_message=query.message)
        
    elif query.data.startswith("coin_"):
        await query.answer()
        parts = query.data.split("_")
        coin, amount = parts[1], parts[2]
        
        await notify_admin(context, message=f"🧾 **INVOICE GENERATED**\n➖➖➖➖➖➖➖➖➖➖\n👤 **User:** {user_display} (`{user_id}`)\n💰 **Amount:** £{amount}\n🪙 **Coin:** {coin}")
        
        await safe_send(context, user_id, "⏳ *Generating invoice...*", lang=lang, edit_message=query.message)
        await asyncio.sleep(1)
        
        addr = {"LTC": LTC_ADDRESS, "BTC": BTC_ADDRESS, "USDT-TRC20": USDT_TRC20_ADDRESS, "USDT-ERC20": USDT_ERC20_ADDRESS, "ETH": ETH_ADDRESS, "SOL": SOL_ADDRESS}.get(coin, "N/A")
        rates_to_gbp = {"LTC": 0.018, "BTC": 0.000021, "USDT-TRC20": 1.28, "USDT-ERC20": 1.28, "ETH": 0.00038, "SOL": 0.0085}
        crypto_amount = float(amount) * rates_to_gbp.get(coin, 1.0)
        
        msg = f"💳 **PAYMENT INVOICE GENERATED**\n➖➖➖➖➖➖➖➖➖➖\n\n🌐 **NETWORK:** {coin}\n⚠️ **WARNING:** Send ONLY **{coin}**.\n\n💰 **AMOUNT DUE:** `{crypto_amount:.4f}` {coin} (£{amount})\n📬 **DEPOSIT ADDRESS:**\n`{addr}`\n\n➖➖➖➖➖➖➖➖➖➖\n⏳ **Status:** Waiting for payment..."
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Check Payment", callback_data="check_payment")], [InlineKeyboardButton("📸 Send Screenshot", callback_data="send_screenshot")], [InlineKeyboardButton("❌ Cancel", callback_data="back_to_main")]])
        await safe_send(context, user_id, msg, markup, lang, edit_message=query.message)
        
    elif query.data == "check_payment":
        error_msg = await translate_text("❌ Error: Payment not found on the blockchain. Please allow 5-15 minutes for confirmations, or use 'Send Screenshot' if you have already paid.", lang)
        await query.answer(error_msg, show_alert=True)
        
    elif query.data == "send_screenshot":
        USER_STATES[user_id] = "awaiting_screenshot"
        msg = "📸 **UPLOAD SCREENSHOT**\n➖➖➖➖➖➖➖➖➖➖\n\nPlease send the transaction screenshot/receipt now."
        await safe_send(context, user_id, msg, InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="back_to_main")]]), lang, edit_message=query.message)
        
    elif query.data == "faq_ask":
        USER_STATES[user_id] = "awaiting_faq_question"
        msg = "❓ **ASK A QUESTION**\n📝 PLEASE TYPE YOUR QUESTION BELOW"
        await safe_send(context, user_id, msg, InlineKeyboardMarkup([[InlineKeyboardButton("❌ CANCEL", callback_data="back_to_main")]]), lang, edit_message=query.message)

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    # Standard Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("purchase", purchase_command)) 
    application.add_handler(CommandHandler("help", help_command)) 
    
    # Catch-all Command block (Must be under the real commands)
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command)) 
    
    # Content Listeners
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_clicks))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(handle_inline_callbacks))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

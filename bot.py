import os
import logging
import asyncio
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
USER_LANGUAGES = {} # Stores user_id -> language code

# Fetch all worldwide supported languages
try:
    SUPPORTED_LANGS = GoogleTranslator().get_supported_languages(as_dict=True)
except:
    SUPPORTED_LANGS = {'english': 'en', 'spanish': 'es', 'french': 'fr', 'chinese (simplified)': 'zh-CN', 'russian': 'ru', 'arabic': 'ar', 'hindi': 'hi'}

# Dynamic Text Templates
DYNAMIC_TEXT = {
    "welcome": ("👋 **WELCOME TO UTILITY PANEL**\n➖➖➖➖➖➖➖➖➖➖\n\n🧠 **SYSTEM STATUS**\n├ 🟢 **STATUS:** Operational\n└ 📈 **UPTIME:** 100%\n\n⚡ **WELCOME, {name}**\n🛡️ **PREMIUM UTILITY SOLUTION**\n\n👇 **TO GET STARTED, USE THE MENU BELOW**"),
    "faq": ("❓ **UTILITY PANEL | FAQ**\n➖➖➖➖➖➖➖➖➖➖\n\n❓ **WHAT IS THIS BOT?**\n├ A premium utility solution for managing automated tasks.\n├ Navigate using the control panel below.\n\n➖➖➖➖➖➖➖➖➖➖"),
    "features": ("⚡ **FEATURES**\n➖➖➖➖➖➖➖➖➖➖\n\n🧠 **SYSTEM STATUS**\n├ 🟢 **STATUS:** Operational\n└ 📈 **UPTIME:** 100%\n\n💬 **OUR UTILITY BOT IS PACKED WITH ADVANCED FEATURES!**"),
    "activate": ("💰 **SELECT SUBSCRIPTION PLAN**\n➖➖➖➖➖➖➖➖➖➖\n\n👇 **CHOOSE AMOUNT:**"),
    "dashboard": ("📊 **UTILITY DASHBOARD**\n➖➖➖➖➖➖➖➖➖➖\n\n⛔ **ACCESS DENIED**\n├ 💳 **NO ACTIVE SUBSCRIPTION**\n└ 🛒 **PURCHASE A PLAN TO CONTINUE**\n\n➖➖➖➖➖➖➖➖➖➖"),
    "support": ("💬 **SUPPORT**\n➖➖➖➖➖➖➖➖➖➖\n\n📡 **SUPPORT STATUS**\n├ 🟢 **STATUS:** Active\n└ ⏱️ **RESPONSE:** 2-6h\n\n💬 **COMMON TOPICS**\n├ • PAYMENT PROCESSING\n├ • SUBSCRIPTION ACTIVATION\n├ • BOT SUPPORT\n└ • TECHNICAL ISSUES\n\nℹ️ **BEFORE CONTACTING**\n├ • CHECK TRANSACTION STATUS\n├ • VERIFY SUBSCRIPTION\n├ • TRY /start COMMAND\n└ • REVIEW FAQ SECTION\n\n➖➖➖➖➖➖➖➖➖➖"),
    "results": ("📈 **RESULTS**\n➖➖➖➖➖➖➖➖➖➖\n\n⭐ **REVIEWS & PERFORMANCE**\n├ • AUTHENTIC USER REVIEWS\n├ • SUCCESS STORIES\n├ • PERFORMANCE STATISTICS\n├ • COMMUNITY DISCUSSIONS\n└ • LATEST UPDATES\n\n🌐 **JOIN OUR COMMUNITY**\n👇 **CLICK BELOW**\n\n➖➖➖➖➖➖➖➖➖➖"),
    "commands": ("📋 **COMMANDS**\n🟢 **OPERATIONAL | 📈 UPTIME: 100%**\n➖➖➖➖➖➖➖➖➖➖\n\n🤖 **MAIN COMMANDS**\n◆ 📓 /help\n◆ ⚙️ /admin")
}

BUTTON_LABELS = {
    "btn_dashboard": "📊 DASHBOARD", "btn_activate": "🔑 ACTIVATE", "btn_features": "⚡ FEATURES",
    "btn_system": "⚙️ SYSTEM", "btn_faq": "❓ FAQ", "btn_results": "📈 RESULTS",
    "btn_commands": "📋 COMMANDS", "btn_profile": "👤 PROFILE", "btn_support": "💬 SUPPORT",
    "btn_language": "🌐 LANGUAGE",
    "label_amt1": "Daily £15", "label_amt2": "Weekly £30", "label_amt3": "Monthly £50",
    "label_amt4": "Yearly £100", "label_amt5": "Lifetime £200",
    "val_amt1": "15", "val_amt2": "30", "val_amt3": "50", "val_amt4": "100", "val_amt5": "200"
}

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
    return markup # Keeps main ReplyKeyboard English

async def safe_send(context, chat_id, text, markup=None, lang='en', edit_message=None):
    trans_text = await translate_text(text, lang)
    trans_markup = await translate_markup(markup, lang)
    
    # Repair Markdown spacing often broken by Google Translate
    trans_text = trans_text.replace("** ", "**").replace(" **", "**")
    
    try:
        if edit_message: await edit_message.edit_text(trans_text, reply_markup=trans_markup, parse_mode="Markdown")
        else: await context.bot.send_message(chat_id=chat_id, text=trans_text, reply_markup=trans_markup, parse_mode="Markdown")
    except Exception as e:
        # Fallback to plain text if markdown parser fails
        if edit_message: await edit_message.edit_text(trans_text, reply_markup=trans_markup)
        else: await context.bot.send_message(chat_id=chat_id, text=trans_text, reply_markup=trans_markup)

# --- Helper Functions ---
def get_back_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])

async def notify_admin(context: ContextTypes.DEFAULT_TYPE, message: str = None, photo: str = None, caption: str = None):
    if ADMIN_ID:
        try:
            if photo: await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=caption, parse_mode="Markdown")
            elif message: await context.bot.send_message(chat_id=ADMIN_ID, text=message, parse_mode="Markdown")
        except: pass

# --- Menu Builders ---
def get_main_menu():
    keyboard = [
        [KeyboardButton(BUTTON_LABELS["btn_dashboard"])],
        [KeyboardButton(BUTTON_LABELS["btn_activate"]), KeyboardButton(BUTTON_LABELS["btn_features"]), KeyboardButton(BUTTON_LABELS["btn_system"])],
        [KeyboardButton(BUTTON_LABELS["btn_faq"]), KeyboardButton(BUTTON_LABELS["btn_results"]), KeyboardButton(BUTTON_LABELS["btn_commands"])],
        [KeyboardButton(BUTTON_LABELS["btn_profile"]), KeyboardButton(BUTTON_LABELS["btn_support"]), KeyboardButton(BUTTON_LABELS["btn_language"])]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_admin_main_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📝 Edit Messages", callback_data="admin_templates"), InlineKeyboardButton("🎛️ Edit Keyboards", callback_data="admin_keyboards")], [InlineKeyboardButton("❌ Close Menu", callback_data="admin_logout")]])

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
        [InlineKeyboardButton("Tier 1 Display", callback_data="kbtn_label_amt1"), InlineKeyboardButton("Tier 1 Value", callback_data="kbtn_val_amt1")],
        [InlineKeyboardButton("Tier 2 Display", callback_data="kbtn_label_amt2"), InlineKeyboardButton("Tier 2 Value", callback_data="kbtn_val_amt2")],
        [InlineKeyboardButton("Tier 3 Display", callback_data="kbtn_label_amt3"), InlineKeyboardButton("Tier 3 Value", callback_data="kbtn_val_amt3")],
        [InlineKeyboardButton("Tier 4 Display", callback_data="kbtn_label_amt4"), InlineKeyboardButton("Tier 4 Value", callback_data="kbtn_val_amt4")],
        [InlineKeyboardButton("Tier 5 Display", callback_data="kbtn_label_amt5"), InlineKeyboardButton("Tier 5 Value", callback_data="kbtn_val_amt5")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_home")]
    ])

def get_tiers_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_LABELS["label_amt1"], callback_data="amt_val1"), InlineKeyboardButton(BUTTON_LABELS["label_amt2"], callback_data="amt_val2")],
        [InlineKeyboardButton(BUTTON_LABELS["label_amt3"], callback_data="amt_val3"), InlineKeyboardButton(BUTTON_LABELS["label_amt4"], callback_data="amt_val4")],
        [InlineKeyboardButton(BUTTON_LABELS["label_amt5"], callback_data="amt_val5")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]
    ])

# --- Core Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    lang = USER_LANGUAGES.get(user.id, 'en')
    welcome_text = DYNAMIC_TEXT["welcome"].replace("{name}", user.first_name)
    USER_STATES[user.id] = None
    await safe_send(context, user.id, welcome_text, get_main_menu(), lang)
    await notify_admin(context, message=f"🔔 **NEW USER ALERT**\n➖➖➖➖➖➖➖➖➖➖\n👤 **User:** {user.first_name}\n🆔 **ID:** `{user.id}`\n└ Started the bot.")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in ADMINS or str(user_id) == str(ADMIN_ID): await show_admin_panel(update, context)
    else:
        USER_STATES[user_id] = "awaiting_admin_password"
        await update.message.reply_text("🔒 **ADMIN AUTHENTICATION**\n\nEnter the admin password to continue:", parse_mode="Markdown")

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = "⚙️ **ADMIN CONTROL PANEL**\n➖➖➖➖➖➖➖➖➖➖\n\nSelect a configuration layer below:"
    markup = get_admin_main_menu()
    if update.message: await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")
    elif update.callback_query: await update.callback_query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

async def handle_menu_clicks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    text = update.message.text
    current_state = USER_STATES.get(user_id)
    lang = USER_LANGUAGES.get(user_id, 'en')
    
    # Handle active system states
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
            await safe_send(context, user_id, "❌ Language not recognized.\nPlease type a valid language name (e.g. Spanish, German, Chinese) or click BACK.", get_back_markup(), lang)
        return

    elif current_state and current_state.startswith("awaiting_edit_"):
        if user_id in ADMINS or str(user_id) == str(ADMIN_ID):
            template_key = current_state.replace("awaiting_edit_", "")
            DYNAMIC_TEXT[template_key] = text
            USER_STATES[user_id] = None
            await update.message.reply_text("✅ **Text Template Updated!**", parse_mode="Markdown")
            await update.message.reply_text("⚙️ **TEMPLATE EDITOR**", reply_markup=get_admin_templates_menu(), parse_mode="Markdown")
        return

    elif current_state and current_state.startswith("awaiting_kbtn_"):
        if user_id in ADMINS or str(user_id) == str(ADMIN_ID):
            label_key = current_state.replace("awaiting_kbtn_", "")
            BUTTON_LABELS[label_key] = text
            USER_STATES[user_id] = None
            await update.message.reply_text("✅ **Keyboard saved!**", parse_mode="Markdown")
            await update.message.reply_text("🎛️ **KEYBOARD EDITOR**", reply_markup=get_admin_keyboards_menu(), parse_mode="Markdown")
        return

    elif current_state == "awaiting_faq_question":
        USER_STATES[user_id] = None
        await safe_send(context, user_id, "✅ **TICKET CREATED**\n➖➖➖➖➖➖➖➖➖➖\n\n📌 **TICKET NUMBER:** #5\n⏳ PLEASE WAIT FOR A RESPONSE", lang=lang)
        await notify_admin(context, message=f"❓ **NEW FAQ QUESTION**\n➖➖➖➖➖➖➖➖➖➖\n👤 **From:** {user_name} (`{user_id}`)\n📝 **Question:**\n{text}")
        return

    USER_STATES[user_id] = None

    # Routing based on main menu text
    if text == BUTTON_LABELS["btn_dashboard"]:
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_LABELS["btn_activate"], callback_data="trigger_payment")], [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])
        await safe_send(context, user_id, DYNAMIC_TEXT["dashboard"], markup, lang)
    
    elif text == BUTTON_LABELS["btn_activate"]:
        await safe_send(context, user_id, DYNAMIC_TEXT["activate"], get_tiers_markup(), lang)
    
    elif text == BUTTON_LABELS["btn_features"]:
        await safe_send(context, user_id, DYNAMIC_TEXT["features"], get_back_markup(), lang)
    
    elif text == BUTTON_LABELS["btn_system"]:
        msg = "⚙️ **SYSTEM STATUS**\n➖➖➖➖➖➖➖➖➖➖\n\n🖥️ **SERVER STATUS**\n├ ✅ **API:** Online\n└ ✅ **SERVICES:** Operational\n\n📊 **PERFORMANCE**\n├ 📶 **UPTIME:** 99.9%\n└ ⚡ **RESPONSE:** < 100ms"
        await safe_send(context, user_id, msg, get_back_markup(), lang)
    
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
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("💰 Deposit", callback_data="trigger_payment")], [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])
        await safe_send(context, user_id, msg, markup, lang)
    
    elif text == BUTTON_LABELS["btn_faq"]:
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❓ ASK A QUESTION", callback_data="faq_ask")], [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])
        await safe_send(context, user_id, DYNAMIC_TEXT["faq"], markup, lang)
        
    elif text == BUTTON_LABELS["btn_language"]:
        USER_STATES[user_id] = "awaiting_language_input"
        msg = "🌐 **LANGUAGE SETTINGS**\n➖➖➖➖➖➖➖➖➖➖\n\nPlease type the name of your language below (e.g., Spanish, French, Chinese, Arabic, Hindi, etc.):"
        await safe_send(context, user_id, msg, get_back_markup(), lang)
        
    else:
        # If user types something random and they are in a translated lang, tell them to use the menu
        await safe_send(context, user_id, "Command not recognized. Please use the layout setup panel lower menu.", lang=lang)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    current_state = USER_STATES.get(user_id)
    lang = USER_LANGUAGES.get(user_id, 'en')
    if current_state == "awaiting_screenshot":
        USER_STATES[user_id] = None
        await safe_send(context, user_id, "✅ **SCREENSHOT RECEIVED**\n➖➖➖➖➖➖➖➖➖➖\n\nYour payment receipt has been successfully submitted to the system.\n⏳ Verification processing window is 15-30 minutes.", lang=lang)
        photo_file_id = update.message.photo[-1].file_id
        await notify_admin(context, photo=photo_file_id, caption=f"📸 **NEW PAYMENT SCREENSHOT**\n👤 **From:** {user_name} (`{user_id}`)\n⚠️ Action required: Verify deposit.")

async def handle_inline_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    lang = USER_LANGUAGES.get(user_id, 'en')
    
    if not query.data.startswith("coin_") and query.data != "check_payment":
        await query.answer()

    if query.data == "back_to_main":
        USER_STATES[user_id] = None
        try: await query.message.delete()
        except: pass
        return

    # Admin Routing (Never Translated)
    if query.data == "admin_home" and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        await show_admin_panel(update, context)
    elif query.data == "admin_templates" and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        await query.message.edit_text("⚙️ **TEMPLATE EDITOR**", reply_markup=get_admin_templates_menu(), parse_mode="Markdown")
    elif query.data == "admin_keyboards" and (user_id in ADMINS or str(user_id) == str(ADMIN_ID)):
        await query.message.edit_text("🎛️ **KEYBOARD BUTTON EDITOR**", reply_markup=get_admin_keyboards_menu(), parse_mode="Markdown")
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
            
    # User Routing (Translated)
    elif query.data == "trigger_payment":
        await safe_send(context, user_id, DYNAMIC_TEXT["activate"], get_tiers_markup(), lang, edit_message=query.message)
        
    elif query.data.startswith("amt_val"):
        idx = query.data.replace("amt_val", "")
        amount = BUTTON_LABELS[f"val_amt{idx}"]
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
        
        # Give translation illusion of loading
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
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_clicks))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(handle_inline_callbacks))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

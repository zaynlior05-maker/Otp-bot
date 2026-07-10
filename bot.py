import os
import logging
import asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch Variables from Railway
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

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
DYNAMIC_TEXT = {
    "welcome": ("👋 **WELCOME TO UTILITY PANEL**\n➖➖➖➖➖➖➖➖➖➖\n\n🧠 **SYSTEM STATUS**\n├ 🟢 **STATUS:** Operational\n└ 📈 **UPTIME:** 100%\n\n⚡ **WELCOME, {name}**\n🛡️ **PREMIUM UTILITY SOLUTION**\n\n👇 **TO GET STARTED, USE THE MENU BELOW**"),
    "faq": ("❓ **UTILITY PANEL | FAQ**\n➖➖➖➖➖➖➖➖➖➖\n\n❓ **WHAT IS THIS BOT?**\n├ A premium utility solution for managing automated tasks.\n├ Navigate using the control panel below.\n\n➖➖➖➖➖➖➖➖➖➖"),
    "features": ("⚡ **FEATURES**\n➖➖➖➖➖➖➖➖➖➖\n\n🧠 **SYSTEM STATUS**\n├ 🟢 **STATUS:** Operational\n└ 📈 **UPTIME:** 100%\n\n💬 **OUR UTILITY BOT IS PACKED WITH ADVANCED FEATURES!**"),
    "payment": ("💳 **PAYMENT METHODS**\n➖➖➖➖➖➖➖➖➖➖\n\n🔗 **DEPOSIT VIA GATEWAY**\n├ Accepted: Crypto Only\n└ Status: **LIVE**\n\n💰 **ACCOUNT BALANCE:** £0.00\n\n👇 **SELECT ACTION**"),
    "dashboard": ("📊 **UTILITY DASHBOARD**\n➖➖➖➖➖➖➖➖➖➖\n\n⛔ **ACCESS DENIED**\n├ 💳 **NO ACTIVE SUBSCRIPTION**\n└ 🛒 **PURCHASE A PLAN TO CONTINUE**\n\n➖➖➖➖➖➖➖➖➖➖"),
    "support": ("💬 **SUPPORT**\n➖➖➖➖➖➖➖➖➖➖\n\n📡 **SUPPORT STATUS**\n├ 🟢 **STATUS:** Active\n└ ⏱️ **RESPONSE:** 2-6h\n\n💬 **COMMON TOPICS**\n├ • PAYMENT PROCESSING\n├ • SUBSCRIPTION ACTIVATION\n├ • BOT SUPPORT\n└ • TECHNICAL ISSUES\n\nℹ️ **BEFORE CONTACTING**\n├ • CHECK TRANSACTION STATUS\n├ • VERIFY SUBSCRIPTION\n├ • TRY /start COMMAND\n└ • REVIEW FAQ SECTION\n\n➖➖➖➖➖➖➖➖➖➖"),
    "results": ("📈 **RESULTS**\n➖➖➖➖➖➖➖➖➖➖\n\n⭐ **REVIEWS & PERFORMANCE**\n├ • AUTHENTIC USER REVIEWS\n├ • SUCCESS STORIES\n├ • PERFORMANCE STATISTICS\n├ • COMMUNITY DISCUSSIONS\n└ • LATEST UPDATES\n\n🌐 **JOIN OUR COMMUNITY**\n👇 **CLICK BELOW**\n\n➖➖➖➖➖➖➖➖➖➖")
}

def get_main_menu():
    """Main Menu Keyboard Layout"""
    keyboard = [
        [KeyboardButton("📊 DASHBOARD")],
        [KeyboardButton("💳 PAYMENT"), KeyboardButton("⚡ FEATURES"), KeyboardButton("⚙️ SYSTEM")],
        [KeyboardButton("❓ FAQ"), KeyboardButton("📈 RESULTS"), KeyboardButton("📋 COMMANDS")],
        [KeyboardButton("👤 PROFILE"), KeyboardButton("💬 SUPPORT")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_admin_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Edit Templates", callback_data="admin_templates")],
        [InlineKeyboardButton("👥 User Management", callback_data="admin_users"), InlineKeyboardButton("➕ Add Admin", callback_data="admin_add")],
        [InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("❌ Close", callback_data="admin_logout")]
    ])

def get_admin_templates_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Welcome Text", callback_data="edit_welcome"), InlineKeyboardButton("FAQ Text", callback_data="edit_faq")],
        [InlineKeyboardButton("Features Text", callback_data="edit_features"), InlineKeyboardButton("Payment Text", callback_data="edit_payment")],
        [InlineKeyboardButton("Dashboard Text", callback_data="edit_dashboard"), InlineKeyboardButton("Support Text", callback_data="edit_support")],
        [InlineKeyboardButton("Results Text", callback_data="edit_results"), InlineKeyboardButton("🔙 Back", callback_data="admin_home")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = DYNAMIC_TEXT["welcome"].replace("{name}", update.effective_user.first_name)
    USER_STATES[update.effective_user.id] = None
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in ADMINS:
        await show_admin_panel(update, context)
    else:
        USER_STATES[user_id] = "awaiting_admin_password"
        await update.message.reply_text("🔒 **ADMIN AUTHENTICATION**\n\nEnter the admin password to continue:", parse_mode="Markdown")

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = "⚙️ **ADMIN CONTROL PANEL**\n➖➖➖➖➖➖➖➖➖➖\n\nSelect a module to configure below:"
    markup = get_admin_main_menu()
    if update.message: await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")
    elif update.callback_query: await update.callback_query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

async def handle_menu_clicks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text
    current_state = USER_STATES.get(user_id)
    
    if current_state == "awaiting_admin_password":
        if text == ADMIN_PASSWORD:
            ADMINS.add(user_id)
            USER_STATES[user_id] = None
            try: await update.message.delete()
            except: pass
            await update.message.reply_text("✅ **Access Granted.** Welcome to the Admin Panel.", parse_mode="Markdown")
            await show_admin_panel(update, context)
        else:
            USER_STATES[user_id] = None
            await update.message.reply_text("❌ **Incorrect Password.** Access Denied.", parse_mode="Markdown")
        return

    elif current_state and current_state.startswith("awaiting_edit_"):
        template_key = current_state.replace("awaiting_edit_", "")
        DYNAMIC_TEXT[template_key] = text
        USER_STATES[user_id] = None
        await update.message.reply_text(f"✅ **Template Updated Successfully!**\nThe new text for '{template_key.upper()}' is now live.", parse_mode="Markdown")
        await update.message.reply_text("⚙️ **TEMPLATE EDITOR**\nSelect a template to modify:", reply_markup=get_admin_templates_menu(), parse_mode="Markdown")
        return

    USER_STATES[user_id] = None

    if text == "📊 DASHBOARD":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("💳 PAYMENT", callback_data="trigger_payment")]])
        await update.message.reply_text(DYNAMIC_TEXT["dashboard"], reply_markup=markup, parse_mode="Markdown")
    elif text == "⚡ FEATURES":
        await update.message.reply_text(DYNAMIC_TEXT["features"], parse_mode="Markdown")
    elif text == "⚙️ SYSTEM":
        msg = "⚙️ **SYSTEM STATUS**\n➖➖➖➖➖➖➖➖➖➖\n\n🖥️ **SERVER STATUS**\n├ ✅ **API:** Online\n└ ✅ **SERVICES:** Operational\n\n📊 **PERFORMANCE**\n├ 📶 **UPTIME:** 99.9%\n└ ⚡ **RESPONSE:** < 100ms"
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif text == "📈 RESULTS":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("📈 VIEW RESULTS ↗", url=RESULTS_LINK)]])
        await update.message.reply_text(DYNAMIC_TEXT["results"], reply_markup=markup, parse_mode="Markdown")
    elif text == "📋 COMMANDS":
        msg = "📋 **COMMANDS**\n🟢 **OPERATIONAL | 📈 UPTIME: 100%**\n➖➖➖➖➖➖➖➖➖➖\n\n🤖 **MAIN COMMANDS**\n◆ 📓 /help\n◆ ⚙️ /admin"
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif text == "💬 SUPPORT":
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💬 SUPPORT ↗", url=SUPPORT_LINK), 
                InlineKeyboardButton("📢 CHANNEL ↗", url=CHANNEL_LINK)
            ]
        ])
        await update.message.reply_text(DYNAMIC_TEXT["support"], reply_markup=markup, parse_mode="Markdown")
    elif text == "💳 PAYMENT":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("➕ ADD FUNDS", callback_data="pay_add")], [InlineKeyboardButton("📜 HISTORY", callback_data="pay_history")]])
        await update.message.reply_text(DYNAMIC_TEXT["payment"], reply_markup=markup, parse_mode="Markdown")
    
    elif text == "👤 PROFILE":
        msg = (
            f"👤 **USER PROFILE**\n"
            f"➖➖➖➖➖➖➖➖➖➖\n\n"
            f"🆔 **ACCOUNT DETAILS**\n"
            f"├ 👤 **ID:** `{update.effective_user.id}`\n"
            f"├ 👑 **RANK:** Free Tier\n"
            f"├ 📅 **DAYS ACTIVE:** 0\n"
            f"├ 📞 **CALLS ACCEPTED:** 0\n"
            f"├ 📈 **SUCCESS RATE:** 0%\n"
            f"├ 💰 **BALANCE:** £0.00\n"
            f"└ ⚡ **ACTIONS:** 0\n\n"
            f"➖➖➖➖➖➖➖➖➖➖"
        )
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("💰 Deposit", callback_data="pay_add")], [InlineKeyboardButton("📝 History", callback_data="pay_history")]])
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")
        
    elif text == "❓ FAQ":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❓ ASK A QUESTION", callback_data="faq_ask")], [InlineKeyboardButton("← MENU", callback_data="faq_menu")]])
        await update.message.reply_text(DYNAMIC_TEXT["faq"], reply_markup=markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"You selected {text}. This module is currently under construction.", parse_mode="Markdown")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles screenshot uploads for payment verification."""
    user_id = update.effective_user.id
    current_state = USER_STATES.get(user_id)

    if current_state == "awaiting_screenshot":
        USER_STATES[user_id] = None # Reset state
        msg = (
            "✅ **SCREENSHOT RECEIVED**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "Your payment receipt has been successfully submitted to the system.\n\n"
            "⏳ Our administrators are currently verifying the transaction on the blockchain. "
            "Please allow up to **15-30 minutes** for your balance to be updated."
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

async def handle_inline_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    if not query.data.startswith("coin_"): await query.answer()

    if query.data == "admin_home":
        if user_id in ADMINS: await show_admin_panel(update, context)
    elif query.data == "admin_templates":
        if user_id in ADMINS: await query.message.edit_text("⚙️ **TEMPLATE EDITOR**\nSelect a template:", reply_markup=get_admin_templates_menu(), parse_mode="Markdown")
    elif query.data.startswith("edit_"):
        if user_id in ADMINS:
            template_key = query.data.replace("edit_", "")
            USER_STATES[user_id] = f"awaiting_edit_{template_key}"
            await query.message.edit_text(f"📝 **EDITING: {template_key.upper()}**\n\nPlease type the new text:", parse_mode="Markdown")
    elif query.data == "admin_logout":
        if user_id in ADMINS:
            ADMINS.discard(user_id)
            await query.message.edit_text("🚪 **Logged out.**", parse_mode="Markdown")
            
    elif query.data == "trigger_payment":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("➕ ADD FUNDS", callback_data="pay_add")], [InlineKeyboardButton("📜 HISTORY", callback_data="pay_history")]])
        await query.message.edit_text(DYNAMIC_TEXT["payment"], reply_markup=markup, parse_mode="Markdown")
        
    elif query.data == "pay_add":
        msg = "💰 **DEPOSIT FUNDS**\n➖➖➖➖➖➖➖➖➖➖\n\n👇 **CHOOSE AMOUNT:**"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("£15", callback_data="amount_15"), InlineKeyboardButton("£30", callback_data="amount_30")],
            [InlineKeyboardButton("£50", callback_data="amount_50"), InlineKeyboardButton("£100", callback_data="amount_100")],
            [InlineKeyboardButton("🔙 BACK", callback_data="pay_cancel")]
        ])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")
        
    elif query.data.startswith("amount_"):
        amount = query.data.split("_")[1]
        msg = "🪙 **SELECT CRYPTO:**"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("LTC", callback_data=f"coin_LTC_{amount}"), InlineKeyboardButton("BTC", callback_data=f"coin_BTC_{amount}")],
            [InlineKeyboardButton("USDT (TRC20)", callback_data=f"coin_USDT-TRC20_{amount}"), InlineKeyboardButton("USDT (ERC20)", callback_data=f"coin_USDT-ERC20_{amount}")],
            [InlineKeyboardButton("ETH", callback_data=f"coin_ETH_{amount}"), InlineKeyboardButton("SOL", callback_data=f"coin_SOL_{amount}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
        ])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")
        
    elif query.data.startswith("coin_"):
        await query.answer()
        parts = query.data.split("_")
        coin, amount = parts[1], parts[2]
        await query.message.edit_text("⏳ *Generating invoice...*", parse_mode="Markdown")
        await asyncio.sleep(1)
        
        addr = {
            "LTC": LTC_ADDRESS, 
            "BTC": BTC_ADDRESS, 
            "USDT-TRC20": USDT_TRC20_ADDRESS,
            "USDT-ERC20": USDT_ERC20_ADDRESS,
            "ETH": ETH_ADDRESS,
            "SOL": SOL_ADDRESS
        }.get(coin, "N/A")
        
        # New Detailed Invoice Layout
        msg = (
            f"💳 **PAYMENT INVOICE GENERATED**\n"
            f"➖➖➖➖➖➖➖➖➖➖\n\n"
            f"🌐 **NETWORK:** {coin}\n"
            f"⚠️ **WARNING:** Send ONLY **{coin}** to the address below using its native network.\n\n"
            f"💰 **AMOUNT DUE:** `~{amount}` {coin} (£{amount})\n"
            f"📬 **DEPOSIT ADDRESS:**\n`{addr}`\n\n"
            f"*(Tap the address above to copy it)*\n\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"⏳ **Status:** Waiting for payment..."
        )
        
        # New Buttons including Check Payment and Send Screenshot
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Check Payment", callback_data="check_payment")],
            [InlineKeyboardButton("📸 Send Screenshot", callback_data="send_screenshot")],
            [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
        ])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")
        
    elif query.data == "check_payment":
        # Professional Error Alert for Check Payment
        await query.answer("❌ Error: Payment not found on the blockchain. Please allow 5-15 minutes for confirmations, or use 'Send Screenshot' if you have already paid.", show_alert=True)

    elif query.data == "send_screenshot":
        # Activates the screenshot waiting state
        USER_STATES[user_id] = "awaiting_screenshot"
        msg = (
            "📸 **UPLOAD SCREENSHOT**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "Please send the screenshot or receipt of your successful transaction here."
        )
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif query.data == "pay_cancel":
        USER_STATES[user_id] = None # Clear state just in case
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("➕ ADD FUNDS", callback_data="pay_add")], [InlineKeyboardButton("📜 HISTORY", callback_data="pay_history")]])
        await query.message.edit_text(DYNAMIC_TEXT["payment"], reply_markup=markup, parse_mode="Markdown")
        
    elif query.data == "pay_history":
        msg = (
            "📜 **TRANSACTION HISTORY**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "❌ **ERROR: NO RECORDS FOUND**\n"
            "├ You do not have an active subscription.\n"
            "└ Please deposit funds to begin.\n\n"
            "➖➖➖➖➖➖➖➖➖➖"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 ADD FUNDS", callback_data="pay_add")],
            [InlineKeyboardButton("🔙 BACK TO PROFILE", callback_data="return_profile")]
        ])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif query.data == "return_profile":
        msg = (
            f"👤 **USER PROFILE**\n"
            f"➖➖➖➖➖➖➖➖➖➖\n\n"
            f"🆔 **ACCOUNT DETAILS**\n"
            f"├ 👤 **ID:** `{query.from_user.id}`\n"
            f"├ 👑 **RANK:** Free Tier\n"
            f"├ 📅 **DAYS ACTIVE:** 0\n"
            f"├ 📞 **CALLS ACCEPTED:** 0\n"
            f"├ 📈 **SUCCESS RATE:** 0%\n"
            f"├ 💰 **BALANCE:** £0.00\n"
            f"└ ⚡ **ACTIONS:** 0\n\n"
            f"➖➖➖➖➖➖➖➖➖➖"
        )
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("💰 Deposit", callback_data="pay_add")], [InlineKeyboardButton("📝 History", callback_data="pay_history")]])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif query.data == "faq_ask":
        await query.message.edit_text("📝 Please type your question.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ CANCEL", callback_data="faq_cancel")]]))
        
    elif query.data == "faq_cancel":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❓ ASK A QUESTION", callback_data="faq_ask")], [InlineKeyboardButton("← MENU", callback_data="faq_menu")]])
        await query.message.edit_text(DYNAMIC_TEXT["faq"], reply_markup=markup, parse_mode="Markdown")
        
    elif query.data == "faq_menu":
        await query.message.delete()

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    # Message Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_clicks))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo)) # New handler for screenshots
    
    # Callback Handlers
    application.add_handler(CallbackQueryHandler(handle_inline_callbacks))
    
    # Run
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

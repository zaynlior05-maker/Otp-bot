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

# Fetch Crypto Wallet Addresses from Railway
LTC_ADDRESS = os.getenv("LTC_ADDRESS", "YOUR_LTC_ADDRESS_NOT_SET")
BTC_ADDRESS = os.getenv("BTC_ADDRESS", "YOUR_BTC_ADDRESS_NOT_SET")
USDT_TRC20_ADDRESS = os.getenv("USDT_TRC20_ADDRESS", "YOUR_USDT_TRC20_ADDRESS_NOT_SET")
USDT_ERC20_ADDRESS = os.getenv("USDT_ERC20_ADDRESS", "YOUR_USDT_ERC20_ADDRESS_NOT_SET")
ETH_ADDRESS = os.getenv("ETH_ADDRESS", "YOUR_ETH_ADDRESS_NOT_SET")

# Global Memory Variables (Resets to these defaults on Railway Restart)
ADMINS = set()
USER_STATES = {}
DYNAMIC_TEXT = {
    "welcome": (
        "👋 **WELCOME TO UTILITY PANEL**\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "🧠 **SYSTEM STATUS**\n"
        "├ 🟢 **STATUS:** Operational\n"
        "└ 📈 **UPTIME:** 100%\n\n"
        "⚡ **WELCOME, {name}**\n"
        "🛡️ **PREMIUM UTILITY SOLUTION**\n\n"
        "👇 **TO GET STARTED, USE THE MENU BELOW**"
    ),
    "faq": (
        "❓ **UTILITY PANEL | FAQ**\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "❓ **WHAT IS THIS BOT?**\n"
        "├ A premium utility solution for managing automated tasks.\n"
        "├ Navigate using the control panel below.\n\n"
        "➖➖➖➖➖➖➖➖➖➖"
    ),
    "features": (
        "⚡ **FEATURES**\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "🧠 **SYSTEM STATUS**\n"
        "├ 🟢 **STATUS:** Operational\n"
        "└ 📈 **UPTIME:** 100%\n\n"
        "💬 **OUR UTILITY BOT IS PACKED WITH ADVANCED FEATURES!**"
    ),
    "payment": (
        "💳 **PAYMENT METHODS**\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "🔗 **DEPOSIT VIA GATEWAY**\n"
        "├ Accepted: Crypto Only\n"
        "└ Status: **LIVE**\n\n"
        "💰 **ACCOUNT BALANCE:** £0.00\n\n"
        "👇 **SELECT ACTION**"
    ),
    "subscription": (
        "🖋️ **SUBSCRIPTION PLANS**\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "💎 **CHOOSE YOUR TIER**\n\n"
        "🟢 **BASIC PLAN**\n"
        "├ Price: £20 / Month\n"
        "└ Access: Standard Features\n\n"
        "🔵 **PRO PLAN**\n"
        "├ Price: £50 / Month\n"
        "└ Access: Advanced + Priority\n\n"
        "👑 **ULTRA PLAN**\n"
        "├ Price: £90 / Month\n"
        "└ Access: Full VIP Access\n\n"
        "➖➖➖➖➖➖➖➖➖➖"
    ),
    "dashboard": (
        "📊 **UTILITY DASHBOARD**\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "⛔ **ACCESS DENIED**\n"
        "├ 💳 **NO ACTIVE SUBSCRIPTION**\n"
        "└ 🛒 **PURCHASE A PLAN TO CONTINUE**\n\n"
        "➖➖➖➖➖➖➖➖➖➖"
    )
}

def get_main_menu():
    keyboard = [
        [KeyboardButton("📊 DASHBOARD")],
        [KeyboardButton("💳 PAYMENT"), KeyboardButton("⚡ FEATURES"), KeyboardButton("⚙️ SYSTEM")],
        [KeyboardButton("🖋️ SUBSCRIPTION")], 
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
        [InlineKeyboardButton("Subscription Text", callback_data="edit_subscription"), InlineKeyboardButton("Dashboard Text", callback_data="edit_dashboard")],
        [InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_home")]
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
    
    if update.message:
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

async def handle_menu_clicks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text
    current_state = USER_STATES.get(user_id)
    
    # --- ADMIN STATE INTERCEPTION ---
    if current_state == "awaiting_admin_password":
        if text == ADMIN_PASSWORD:
            ADMINS.add(user_id)
            USER_STATES[user_id] = None
            try:
                await update.message.delete()
            except:
                pass
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

    # --- REGULAR USER MENU HANDLING ---
    USER_STATES[user_id] = None

    if text == "📊 DASHBOARD":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("💳 PAYMENT", callback_data="trigger_payment")]])
        await update.message.reply_text(DYNAMIC_TEXT["dashboard"], reply_markup=markup, parse_mode="Markdown")

    elif text == "⚡ FEATURES":
        await update.message.reply_text(DYNAMIC_TEXT["features"], parse_mode="Markdown")

    elif text == "⚙️ SYSTEM":
        msg = "⚙️ **SYSTEM STATUS**\n➖➖➖➖➖➖➖➖➖➖\n\n🖥️ **SERVER STATUS**\n├ ✅ **API:** Online\n├ ✅ **DATABASE:** Connected\n├ ✅ **SERVICES:** Operational\n└ ✅ **PAYMENTS:** Active\n\n📊 **PERFORMANCE**\n├ 📶 **UPTIME:** 99.9%\n├ ⚡ **RESPONSE:** < 100ms\n└ 🔄 **LAST CHECK:** Just now\n\n➖➖➖➖➖➖➖➖➖➖"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "📈 RESULTS":
        msg = "📈 **RESULTS**\n➖➖➖➖➖➖➖➖➖➖\n\n⭐ **REVIEWS & PERFORMANCE**\n├ • AUTHENTIC USER REVIEWS\n├ • SUCCESS STORIES\n├ • PERFORMANCE STATISTICS\n├ • COMMUNITY DISCUSSIONS\n└ • LATEST UPDATES\n\n🌐 **JOIN OUR COMMUNITY**\n👇 **CLICK BELOW**\n\n➖➖➖➖➖➖➖➖➖➖"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("VIEW RESULTS ↗", url="https://github.com")]])
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif text == "📋 COMMANDS":
        msg = "📋 **COMMANDS**\n🟢 **OPERATIONAL | 📈 UPTIME: 100%**\n➖➖➖➖➖➖➖➖➖➖\n\n🤖 **MAIN COMMANDS**\n◆ 📓 /help | **VIEW COMMAND LIST**\n◆ 🛒 /purchase | **PURCHASE ACCESS**\n◆ ⚙️ /admin | **ADMIN PANEL**"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "💬 SUPPORT":
        msg = "💬 **SUPPORT**\n➖➖➖➖➖➖➖➖➖➖\n\n📡 **SUPPORT STATUS**\n├ 🟢 **STATUS:** Active\n└ ⏱️ **RESPONSE:** 2-6h\n\n💬 **COMMON TOPICS**\n├ • PAYMENT PROCESSING\n├ • SUBSCRIPTION ACTIVATION\n├ • BOT SUPPORT\n└ • TECHNICAL ISSUES\n\nℹ️ **BEFORE CONTACTING**\n├ • CHECK TRANSACTION STATUS\n├ • VERIFY SUBSCRIPTION\n├ • TRY /start COMMAND\n└ • REVIEW FAQ SECTION\n\n➖➖➖➖➖➖➖➖➖➖"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("💬 SUPPORT ↗", url="https://t.me/telegram"), InlineKeyboardButton("📢 CHANNEL ↗", url="https://t.me/telegram")]])
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif text == "🖋️ SUBSCRIPTION":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("💳 BUY BASIC (£20)", callback_data="sub_basic")], [InlineKeyboardButton("💳 BUY PRO (£50)", callback_data="sub_pro")], [InlineKeyboardButton("💳 BUY ULTRA (£90)", callback_data="sub_ultra")]])
        await update.message.reply_text(DYNAMIC_TEXT["subscription"], reply_markup=markup, parse_mode="Markdown")

    elif text == "💳 PAYMENT":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("➕ ADD FUNDS", callback_data="pay_add")], [InlineKeyboardButton("📜 HISTORY", callback_data="pay_history")]])
        await update.message.reply_text(DYNAMIC_TEXT["payment"], reply_markup=markup, parse_mode="Markdown")
        
    elif text == "👤 PROFILE":
        msg = f"👤 **USER PROFILE**\n➖➖➖➖➖➖➖➖➖➖\n\n🆔 **ACCOUNT DETAILS**\n├ 👤 **ID:** `{update.effective_user.id}`\n├ 👑 **STATUS:** Free Tier\n├ 💰 **BALANCE:** £0.00\n├ ⚡ **ACTIONS USED:** 0\n└ ⏱️ **UPTIME USED:** 0 mins\n\n➖➖➖➖➖➖➖➖➖➖"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("💰 Deposit", callback_data="pay_add"), InlineKeyboardButton("⭐ Upgrade Plan", callback_data="sub_pro")], [InlineKeyboardButton("📝 Transaction History", callback_data="pay_history")]])
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")
        
    elif text == "❓ FAQ":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❓ ASK A QUESTION", callback_data="faq_ask")], [InlineKeyboardButton("← MENU", callback_data="faq_menu")]])
        await update.message.reply_text(DYNAMIC_TEXT["faq"], reply_markup=markup, parse_mode="Markdown")

    else:
        await update.message.reply_text(f"You selected {text}. This module is currently under construction.", parse_mode="Markdown")

async def handle_inline_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    
    # Do not answer query immediately for coin selection so we can show loading screen
    if not query.data.startswith("coin_"):
        await query.answer()

    # --- ADMIN CALLBACKS ---
    if query.data == "admin_home":
        if user_id in ADMINS:
            await show_admin_panel(update, context)

    elif query.data == "admin_templates":
        if user_id in ADMINS:
            await query.message.edit_text("⚙️ **TEMPLATE EDITOR**\n➖➖➖➖➖➖➖➖➖➖\n\nSelect a template below to modify its text:", reply_markup=get_admin_templates_menu(), parse_mode="Markdown")

    elif query.data.startswith("edit_"):
        if user_id in ADMINS:
            template_key = query.data.replace("edit_", "")
            USER_STATES[user_id] = f"awaiting_edit_{template_key}"
            
            instruction = f"📝 **EDITING: {template_key.upper()}**\n➖➖➖➖➖➖➖➖➖➖\n\nPlease type and send the new text for this module now.\n\n*(Tip: You can use Markdown for bolding/lists)*"
            if template_key == "welcome":
                instruction += "\n\n*(Note: Include `{name}` in your text where you want the user's first name to appear!)*"
                
            await query.message.edit_text(instruction, parse_mode="Markdown")

    elif query.data in ["admin_users", "admin_add", "admin_settings", "admin_broadcast"]:
        if user_id in ADMINS:
            await query.answer("🚧 This admin module is under construction.", show_alert=True)
            
    elif query.data == "admin_logout":
        if user_id in ADMINS:
            ADMINS.discard(user_id)
            await query.message.edit_text("🚪 **You have successfully logged out of the Admin Panel.**", parse_mode="Markdown")

    # --- PAYMENT & CRYPTO CALLBACKS ---
    elif query.data.startswith("sub_"):
        await query.answer("💳 Redirecting to payment processor...", show_alert=True)
        
    elif query.data == "pay_add":
        msg = "💰 **DEPOSIT FUNDS**\n➖➖➖➖➖➖➖➖➖➖\n\n💵 **SELECT DEPOSIT AMOUNT**\n├ Minimum Deposit: £15\n└ Currency: GBP (£)\n\n👇 **CHOOSE AN AMOUNT BELOW**\n➖➖➖➖➖➖➖➖➖➖"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("£15", callback_data="amount_15"), InlineKeyboardButton("£30", callback_data="amount_30")], 
            [InlineKeyboardButton("£50", callback_data="amount_50"), InlineKeyboardButton("£100", callback_data="amount_100")], 
            [InlineKeyboardButton("🔙 BACK", callback_data="pay_cancel")]
        ])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif query.data.startswith("amount_"):
        amount = query.data.split("_")[1]
        msg = "🪙 **SELECT CRYPTOCURRENCY**\n➖➖➖➖➖➖➖➖➖➖\n\nPlease select a cryptocurrency for your deposit:\n\n*(Note: Make sure to select the correct network!)*"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("LTC", callback_data=f"coin_LTC_{amount}"), InlineKeyboardButton("BTC", callback_data=f"coin_BTC_{amount}")],
            [InlineKeyboardButton("USDT (TRC20)", callback_data=f"coin_USDT-TRC20_{amount}"), InlineKeyboardButton("USDT (ERC20)", callback_data=f"coin_USDT-ERC20_{amount}")],
            [InlineKeyboardButton("ETH", callback_data=f"coin_ETH_{amount}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
        ])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif query.data.startswith("coin_"):
        # Answer the query manually since we skipped it above
        await query.answer()
        
        parts = query.data.split("_")
        coin = parts[1]
        amount = parts[2]

        # Simulating the generating invoice screen
        await query.message.edit_text("⏳ *Hold on, generating invoice...*", parse_mode="Markdown")
        await asyncio.sleep(1.5)

        # Mapping to the correct address from Railway variables
        address = "NOT_SET"
        if coin == "LTC": address = LTC_ADDRESS
        elif coin == "BTC": address = BTC_ADDRESS
        elif coin == "USDT-TRC20": address = USDT_TRC20_ADDRESS
        elif coin == "USDT-ERC20": address = USDT_ERC20_ADDRESS
        elif coin == "ETH": address = ETH_ADDRESS

        # Rough conversion estimates just for visual display (e.g. £15 to Crypto)
        conversion_rates = {"LTC": 0.018, "BTC": 0.000021, "USDT-TRC20": 1.28, "USDT-ERC20": 1.28, "ETH": 0.00038}
        estimated_crypto = float(amount) * conversion_rates.get(coin, 1)

        msg = (
            f"🪙 **{coin} DEPOSIT**\n"
            f"➖➖➖➖➖➖➖➖➖➖\n\n"
            f"⚠️ **WARNING:** Send ONLY **{coin}** to this address. Sending any other coin will result in permanent loss.\n\n"
            f"💰 **Amount Expected:** `~{estimated_crypto:.4f}` {coin} (£{amount})\n"
            f"📬 **Deposit Address:**\n`{address}`\n\n"
            f"*(Tap the address above to copy it)*\n\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"⏳ Waiting for payment..."
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Check Payment", callback_data="check_payment")],
            [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
        ])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif query.data == "check_payment":
        await query.answer("⏳ Payment not detected on the blockchain yet. Please allow 5-15 minutes for confirmations.", show_alert=True)

    elif query.data == "pay_cancel":
        # Returns user to the base payment menu
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("➕ ADD FUNDS", callback_data="pay_add")], [InlineKeyboardButton("📜 HISTORY", callback_data="pay_history")]])
        await query.message.edit_text(DYNAMIC_TEXT["payment"], reply_markup=markup, parse_mode="Markdown")

    # --- MISC CALLBACKS ---
    elif query.data == "pay_history":
        await query.answer("📜 No transaction records found.", show_alert=True)
        
    elif query.data == "faq_ask":
        await query.message.edit_text("📝 Please type your question.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ CANCEL", callback_data="faq_cancel")]]))
    elif query.data == "faq_cancel":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❓ ASK A QUESTION", callback_data="faq_ask")], [InlineKeyboardButton("← MENU", callback_data="faq_menu")]])
        await query.message.edit_text(DYNAMIC_TEXT["faq"], reply_markup=markup, parse_mode="Markdown")
    elif query.data == "faq_menu":
        await query.message.delete()
        
    elif query.data == "trigger_payment":
        await query.answer("💳 Directing to Payment Gateway...", show_alert=True)

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("admin", admin_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_clicks))
    application.add_handler(CallbackQueryHandler(handle_inline_callbacks))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

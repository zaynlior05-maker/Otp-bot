import os
import logging
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
        "├ Accepted: Crypto / Cards\n"
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
        [KeyboardButton("🖋️ SUBSCRIPTION"), KeyboardButton("🔑 ACTIVATE")],
        [KeyboardButton("❓ FAQ"), KeyboardButton("📈 RESULTS"), KeyboardButton("📋 COMMANDS")],
        [KeyboardButton("👤 PROFILE"), KeyboardButton("💬 SUPPORT"), KeyboardButton("🤝 PARTNER")]
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
    # Replaces {name} with the user's actual first name dynamically
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
        # Return to templates menu
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

    elif text == "🤝 PARTNER":
        bot_username = context.bot.username if context.bot.username else "UtilityBot"
        msg = f"🤝 **PARTNER PANEL**\n➖➖➖➖➖➖➖➖➖➖\n\n🔗 **YOUR REFERRAL LINK:**\n`https://t.me/{bot_username}?start=ref_{update.effective_user.id}`\n\n➖➖➖➖➖➖➖➖➖➖\n📊 **CLICK STATISTICS:**\n├ 📅 **TODAY:** 0 clicks\n├ 📅 **THIS WEEK:** 0 clicks\n├ 📅 **THIS MONTH:** 0 clicks\n└ 📈 **ALL TIME:** 0 clicks\n\n👥 **REFERRAL STATS:**\n├ 👤 **TOTAL USERS:** 0 users\n├ 📊 **CONVERSION:** 0.0%\n└ 💎 **COMMISSION RATE:** 50%\n\n➖➖➖➖➖➖➖➖➖➖\n💰 **EARNINGS:**\n├ 📅 **TODAY:** £0.00\n├ 📅 **THIS WEEK:** £0.00\n├ 📅 **THIS MONTH:** £0.00\n└ 💵 **ALL TIME:** £0.00\n\n➖➖➖➖➖➖➖➖➖➖"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("📊 Generate Stats Image", callback_data="partner_image"), InlineKeyboardButton("📩 Download CSV Report", callback_data="partner_csv")], [InlineKeyboardButton("🔄 Refresh Stats", callback_data="partner_refresh")]])
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

    # --- NORMAL CALLBACKS ---
    elif query.data.startswith("sub_"):
        await query.answer("💳 Redirecting to payment processor...", show_alert=True)
        
    elif query.data == "pay_add":
        msg = "💰 **DEPOSIT FUNDS**\n➖➖➖➖➖➖➖➖➖➖\n\n💵 **SELECT DEPOSIT AMOUNT**\n├ Minimum Deposit: £15\n└ Currency: GBP (£)\n\n👇 **CHOOSE AN AMOUNT BELOW**\n➖➖➖➖➖➖➖➖➖➖"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("£15", callback_data="dep_15"), InlineKeyboardButton("£30", callback_data="dep_30")], [InlineKeyboardButton("£50", callback_data="dep_50"), InlineKeyboardButton("£100", callback_data="dep_100")], [InlineKeyboardButton("💳 PAY WITH CARD", callback_data="dep_card")], [InlineKeyboardButton("🪙 PAY WITH CRYPTO", callback_data="dep_crypto")], [InlineKeyboardButton("🔙 BACK", callback_data="pay_back")]])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif query.data == "pay_back":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("➕ ADD FUNDS", callback_data="pay_add")], [InlineKeyboardButton("📜 HISTORY", callback_data="pay_history")]])
        await query.message.edit_text(DYNAMIC_TEXT["payment"], reply_markup=markup, parse_mode="Markdown")
        
    elif query.data.startswith("dep_"):
        await query.answer("🔄 Generating deposit invoice...", show_alert=True)

    elif query.data == "pay_history":
        await query.answer("📜 No transaction records found.", show_alert=True)
        
    elif query.data == "partner_image":
        await query.answer("🖼️ Generating image...", show_alert=True)
    elif query.data == "partner_csv":
        await query.answer("📩 CSV generation pending.", show_alert=True)
    elif query.data == "partner_refresh":
        await query.answer("🔄 Stats refreshed successfully.", show_alert=False)
        
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

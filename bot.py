import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch Token
TOKEN = os.getenv("BOT_TOKEN")

def get_main_menu():
    """Generates the persistent bottom keyboard layout."""
    keyboard = [
        [KeyboardButton("📊 DASHBOARD")],
        [KeyboardButton("💳 PAYMENT"), KeyboardButton("⚡ FEATURES"), KeyboardButton("⚙️ SYSTEM")],
        [KeyboardButton("🖋️ SUBSCRIPTION"), KeyboardButton("🔑 ACTIVATE")],
        [KeyboardButton("❓ FAQ"), KeyboardButton("📈 RESULTS"), KeyboardButton("📋 COMMANDS")],
        [KeyboardButton("👤 PROFILE"), KeyboardButton("💬 SUPPORT"), KeyboardButton("🤝 PARTNER")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_faq_text():
    return (
        "❓ **UTILITY PANEL | FAQ**\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "❓ **WHAT IS THIS BOT?**\n"
        "├ A premium utility solution for managing automated tasks.\n"
        "├ Navigate using the control panel below.\n\n"
        "➖➖➖➖➖➖➖➖➖➖"
    )

def get_faq_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ ASK A QUESTION", callback_data="faq_ask")],
        [InlineKeyboardButton("← MENU", callback_data="faq_menu")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        f"👋 **WELCOME TO UTILITY PANEL**\n"
        f"➖➖➖➖➖➖➖➖➖➖\n\n"
        f"🧠 **SYSTEM STATUS**\n"
        f"├ 🟢 **STATUS:** Operational\n"
        f"└ 📈 **UPTIME:** 100%\n\n"
        f"⚡ **WELCOME, {update.effective_user.first_name}**\n"
        f"🛡️ **PREMIUM UTILITY SOLUTION**\n\n"
        f"👇 **TO GET STARTED, USE THE MENU BELOW**"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

async def handle_menu_clicks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text == "📊 DASHBOARD":
        msg = (
            "📊 **UTILITY DASHBOARD**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "⛔ **ACCESS DENIED**\n"
            "├ 💳 **NO ACTIVE SUBSCRIPTION**\n"
            "└ 🛒 **PURCHASE A PLAN TO CONTINUE**\n\n"
            "➖➖➖➖➖➖➖➖➖➖"
        )
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("💳 PAYMENT", callback_data="trigger_payment")]])
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif text == "⚡ FEATURES":
        msg = (
            "⚡ **FEATURES**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "🧠 **SYSTEM STATUS**\n"
            "├ 🟢 **STATUS:** Operational\n"
            "└ 📈 **UPTIME:** 100%\n\n"
            "💬 **OUR UTILITY BOT IS PACKED WITH ADVANCED FEATURES!**"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "⚙️ SYSTEM":
        msg = (
            "⚙️ **SYSTEM STATUS**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "🖥️ **SERVER STATUS**\n"
            "├ ✅ **API:** Online\n"
            "├ ✅ **DATABASE:** Connected\n"
            "├ ✅ **SERVICES:** Operational\n"
            "└ ✅ **PAYMENTS:** Active\n\n"
            "📊 **PERFORMANCE**\n"
            "├ 📶 **UPTIME:** 99.9%\n"
            "├ ⚡ **RESPONSE:** < 100ms\n"
            "└ 🔄 **LAST CHECK:** Just now\n\n"
            "➖➖➖➖➖➖➖➖➖➖"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "📈 RESULTS":
        msg = (
            "📈 **RESULTS**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "⭐ **REVIEWS & PERFORMANCE**\n"
            "├ • AUTHENTIC USER REVIEWS\n"
            "├ • SUCCESS STORIES\n"
            "├ • PERFORMANCE STATISTICS\n"
            "├ • COMMUNITY DISCUSSIONS\n"
            "└ • LATEST UPDATES\n\n"
            "🌐 **JOIN OUR COMMUNITY**\n"
            "👇 **CLICK BELOW**\n\n"
            "➖➖➖➖➖➖➖➖➖➖"
        )
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("VIEW RESULTS ↗", url="https://github.com")]])
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif text == "📋 COMMANDS":
        msg = (
            "📋 **COMMANDS**\n"
            "🟢 **OPERATIONAL | 📈 UPTIME: 100%**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "🤖 **MAIN COMMANDS**\n"
            "◆ 📓 /help | **VIEW COMMAND LIST**\n"
            "◆ 🛒 /purchase | **PURCHASE ACCESS**"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "💬 SUPPORT":
        msg = (
            "💬 **SUPPORT**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "📡 **SUPPORT STATUS**\n"
            "├ 🟢 **STATUS:** Active\n"
            "└ ⏱️ **RESPONSE:** 2-6h\n\n"
            "💬 **COMMON TOPICS**\n"
            "├ • PAYMENT PROCESSING\n"
            "├ • SUBSCRIPTION ACTIVATION\n"
            "├ • BOT SUPPORT\n"
            "└ • TECHNICAL ISSUES\n\n"
            "ℹ️ **BEFORE CONTACTING**\n"
            "├ • CHECK TRANSACTION STATUS\n"
            "├ • VERIFY SUBSCRIPTION\n"
            "├ • TRY /start COMMAND\n"
            "└ • REVIEW FAQ SECTION\n\n"
            "➖➖➖➖➖➖➖➖➖➖"
        )
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💬 SUPPORT ↗", url="https://t.me/telegram"), 
                InlineKeyboardButton("📢 CHANNEL ↗", url="https://t.me/telegram")
            ]
        ])
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif text == "🤝 PARTNER":
        bot_username = context.bot.username if context.bot.username else "UtilityBot"
        msg = (
            "🤝 **PARTNER PANEL**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "🔗 **YOUR REFERRAL LINK:**\n"
            f"`https://t.me/{bot_username}?start=ref_{update.effective_user.id}`\n\n"
            "➖➖➖➖➖➖➖➖➖➖\n"
            "📊 **CLICK STATISTICS:**\n"
            "├ 📅 **TODAY:** 0 clicks\n"
            "├ 📅 **THIS WEEK:** 0 clicks\n"
            "├ 📅 **THIS MONTH:** 0 clicks\n"
            "└ 📈 **ALL TIME:** 0 clicks\n\n"
            "👥 **REFERRAL STATS:**\n"
            "├ 👤 **TOTAL USERS:** 0 users\n"
            "├ 📊 **CONVERSION:** 0.0%\n"
            "└ 💎 **COMMISSION RATE:** 50%\n\n"
            "➖➖➖➖➖➖➖➖➖➖\n"
            "💰 **EARNINGS:**\n"
            "├ 📅 **TODAY:** £0.00\n"
            "├ 📅 **THIS WEEK:** £0.00\n"
            "├ 📅 **THIS MONTH:** £0.00\n"
            "└ 💵 **ALL TIME:** £0.00\n\n"
            "➖➖➖➖➖➖➖➖➖➖"
        )
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Generate Stats Image", callback_data="partner_image"),
                InlineKeyboardButton("📩 Download CSV Report", callback_data="partner_csv")
            ],
            [InlineKeyboardButton("🔄 Refresh Stats", callback_data="partner_refresh")]
        ])
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif text == "🖋️ SUBSCRIPTION":
        msg = (
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
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 BUY BASIC (£20)", callback_data="sub_basic")],
            [InlineKeyboardButton("💳 BUY PRO (£50)", callback_data="sub_pro")],
            [InlineKeyboardButton("💳 BUY ULTRA (£90)", callback_data="sub_ultra")]
        ])
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif text == "💳 PAYMENT":
        msg = (
            "💳 **PAYMENT METHODS**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "🔗 **DEPOSIT VIA GATEWAY**\n"
            "├ Accepted: Crypto / Cards\n"
            "└ Status: **LIVE**\n\n"
            "💰 **ACCOUNT BALANCE:** £0.00\n\n"
            "👇 **SELECT ACTION**"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ ADD FUNDS", callback_data="pay_add")],
            [InlineKeyboardButton("📜 HISTORY", callback_data="pay_history")]
        ])
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")
        
    elif text == "👤 PROFILE":
        msg = (
            "👤 **USER PROFILE**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "🆔 **ACCOUNT DETAILS**\n"
            f"├ 👤 **ID:** `{update.effective_user.id}`\n"
            "├ 👑 **STATUS:** Free Tier\n"
            "├ 💰 **BALANCE:** £0.00\n"
            "├ ⚡ **ACTIONS USED:** 0\n"
            "└ ⏱️ **UPTIME USED:** 0 mins\n\n"
            "➖➖➖➖➖➖➖➖➖➖"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Deposit", callback_data="pay_add"), InlineKeyboardButton("⭐ Upgrade Plan", callback_data="sub_pro")],
            [InlineKeyboardButton("📝 Transaction History", callback_data="pay_history")]
        ])
        await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")
        
    elif text == "❓ FAQ":
        await update.message.reply_text(get_faq_text(), reply_markup=get_faq_keyboard(), parse_mode="Markdown")

    else:
        await update.message.reply_text(f"You selected {text}. This module is currently under construction.", parse_mode="Markdown")

async def handle_inline_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Subscription Callbacks
    if query.data.startswith("sub_"):
        await query.answer("💳 Redirecting to payment processor...", show_alert=True)
        
    # Payment Callbacks
    elif query.data == "pay_add":
        msg = (
            "💰 **DEPOSIT FUNDS**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "💵 **SELECT DEPOSIT AMOUNT**\n"
            "├ Minimum Deposit: £15\n"
            "└ Currency: GBP (£)\n\n"
            "👇 **CHOOSE AN AMOUNT BELOW**\n"
            "➖➖➖➖➖➖➖➖➖➖"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("£15", callback_data="dep_15"), InlineKeyboardButton("£30", callback_data="dep_30")],
            [InlineKeyboardButton("£50", callback_data="dep_50"), InlineKeyboardButton("£100", callback_data="dep_100")],
            [InlineKeyboardButton("💳 PAY WITH CARD", callback_data="dep_card")],
            [InlineKeyboardButton("🪙 PAY WITH CRYPTO", callback_data="dep_crypto")],
            [InlineKeyboardButton("🔙 BACK", callback_data="pay_back")]
        ])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

    elif query.data == "pay_back":
        msg = (
            "💳 **PAYMENT METHODS**\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "🔗 **DEPOSIT VIA GATEWAY**\n"
            "├ Accepted: Crypto / Cards\n"
            "└ Status: **LIVE**\n\n"
            "💰 **ACCOUNT BALANCE:** £0.00\n\n"
            "👇 **SELECT ACTION**"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ ADD FUNDS", callback_data="pay_add")],
            [InlineKeyboardButton("📜 HISTORY", callback_data="pay_history")]
        ])
        await query.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")
        
    elif query.data.startswith("dep_"):
        await query.answer("🔄 Generating deposit invoice...", show_alert=True)

    elif query.data == "pay_history":
        await query.answer("📜 No transaction records found.", show_alert=True)
        
    # Partner Callbacks
    elif query.data == "partner_image":
        await query.answer("🖼️ Generating image...", show_alert=True)
    elif query.data == "partner_csv":
        await query.answer("📩 CSV generation pending.", show_alert=True)
    elif query.data == "partner_refresh":
        await query.answer("🔄 Stats refreshed successfully.", show_alert=False)
        
    # FAQ Callbacks
    elif query.data == "faq_ask":
        await query.message.edit_text("📝 Please type your question.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ CANCEL", callback_data="faq_cancel")]]))
    elif query.data == "faq_cancel":
        await query.message.edit_text(get_faq_text(), reply_markup=get_faq_keyboard(), parse_mode="Markdown")
    elif query.data == "faq_menu":
        await query.message.delete()
        
    # Miscellaneous
    elif query.data == "trigger_payment":
        await query.answer("💳 Directing to Payment Gateway...", show_alert=True)

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_clicks))
    application.add_handler(CallbackQueryHandler(handle_inline_callbacks))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

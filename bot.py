import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID")

UPI_ID = os.getenv("UPI_ID", "Varsha310@upi")
PRICE = "₹99"
MEMBERSHIP = "1 Year"

pending_users = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💎 1 Year Membership – ₹99", callback_data="buy")],
        [InlineKeyboardButton("📞 Video Call", callback_data="info")],
        [InlineKeyboardButton("🎬 Videos & Photos", callback_data="info")],
    ]

    await update.message.reply_text(
        "🌟 PREMIUM MEMBERSHIP 🌟\n\n"
        "💰 Price: ₹99\n"
        "📅 Validity: 1 Year\n\n"
        "📞 Video Call\n"
        "🎬 Videos\n"
        "📸 Photos\n\n"
        "Payment ke baad manual approval milega.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        pending_users.add(query.from_user.id)

        keyboard = [
            [InlineKeyboardButton("💳 Payment Done", callback_data="paid")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")],
        ]

        await query.edit_message_text(
            "💎 1 YEAR MEMBERSHIP\n\n"
            f"💰 Amount: {PRICE}\n"
            f"📲 UPI ID: {UPI_ID}\n\n"
            "1️⃣ UPI par ₹99 payment karo\n"
            "2️⃣ Payment ka screenshot yahan bhejo\n"
            "3️⃣ Admin manual approval karega\n"
            "4️⃣ Approval ke baad private channel link milega\n\n"
            "⚠️ Payment verify hone ke baad hi access diya jayega.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data == "paid":
        await query.message.reply_text(
            "✅ Payment karne ke baad isi chat me payment ka screenshot bhejo.\n\n"
            "Screenshot milte hi admin verification karega."
        )

    elif query.data == "info":
        await query.answer("₹99 me 1 year membership available hai.", show_alert=True)

    elif query.data == "back":
        await start_from_callback(query)


async def start_from_callback(query):
    keyboard = [
        [InlineKeyboardButton("💎 1 Year Membership – ₹99", callback_data="buy")],
        [InlineKeyboardButton("📞 Video Call", callback_data="info")],
        [InlineKeyboardButton("🎬 Videos & Photos", callback_data="info")],
    ]

    await query.edit_message_text(
        "🌟 PREMIUM MEMBERSHIP 🌟\n\n"
        "💰 ₹99 / 1 Year\n"
        "📞 Video Call\n"
        "🎬 Videos\n"
        "📸 Photos",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id not in pending_users:
        await update.message.reply_text(
            "Pehle membership button se payment process start karo."
        )
        return

    if not update.message.photo:
        return

    photo = update.message.photo[-1]

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ APPROVE",
                callback_data=f"approve:{user.id}"
            ),
            InlineKeyboardButton(
                "❌ REJECT",
                callback_data=f"reject:{user.id}"
            ),
        ]
    ]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=(
            "💳 NEW PAYMENT\n\n"
            f"👤 Name: {user.full_name}\n"
            f"🆔 User ID: {user.id}\n"
            f"🔗 Username: @{user.username or 'N/A'}\n"
            f"💰 Amount: {PRICE}"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    await update.message.reply_text(
        "📨 Payment screenshot admin ko bhej diya gaya hai.\n"
        "Verification ke baad private channel link milega."
    )


async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Admin only", show_alert=True)
        return

    action, user_id_text = query.data.split(":")
    user_id = int(user_id_text)

    if action == "reject":
        pending_users.discard(user_id)

        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Payment verify nahi ho paya. Please admin se contact karein."
        )

        await query.edit_message_caption(
            caption="❌ PAYMENT REJECTED

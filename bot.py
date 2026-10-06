import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# اطلاعات موقت سفارش‌ها
orders = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if context.args:
        order_id = context.args[0]

        orders[order_id] = {
            "user_id": user.id,
            "username": user.username,
        }

        await update.message.reply_text(
            f"🛍 سفارش شما\n\n"
            f"شماره سفارش: #{order_id}\n\n"
            f"اطلاعات کامل محصول و مبلغ پرداختی از سایت دریافت خواهد شد.\n\n"
            f"💳 بعد از نمایش مبلغ، پرداخت را انجام دهید و رسید را همینجا ارسال کنید."
        )
    else:
        await update.message.reply_text(
            "سلام 👋\n"
            "به فروشگاه رایکاه خوش آمدید.\n\n"
            "برای ثبت سفارش، ابتدا محصول موردنظر را از سایت انتخاب کنید."
        )


async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not update.message.photo:
        return

    photo = update.message.photo[-1]

    caption = (
        "🔔 رسید پرداخت جدید\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🆔 User ID: {user.id}\n"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ تأیید پرداخت",
                callback_data=f"approve_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ رد پرداخت",
                callback_data=f"reject_{user.id}"
            ),
        ]
    ])

    if ADMIN_ID:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo.file_id,
            caption=caption,
            reply_markup=keyboard,
        )

    await update.message.reply_text(
        "✅ رسید شما دریافت شد.\n\n"
        "رسید برای بررسی ارسال شد. پس از تأیید، نتیجه از طریق همین ربات به شما اعلام می‌شود."
    )


async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("دسترسی ندارید.", show_alert=True)
        return

    await query.answer()

    action, user_id = query.data.split("_", 1)

    if action == "approve":
        text = (
            "✅ پرداخت تأیید شد.\n\n"
            "سفارش شما با موفقیت ثبت شد.\n"
            "به‌زودی مراحل آماده‌سازی سفارش انجام می‌شود."
        )

        await context.bot.send_message(
            chat_id=int(user_id),
            text=text
        )

        await query.edit_message_caption(
            caption=query.message.caption + "\n\n✅ پرداخت تأیید شد."
        )

    elif action == "reject":
        text = (
            "❌ پرداخت شما تأیید نشد.\n\n"
            "لطفاً رسید پرداخت را بررسی کرده و در صورت نیاز مجدداً ارسال کنید."
        )

        await context.bot.send_message(
            chat_id=int(user_id),
            text=text
        )

        await query.edit_message_caption(
            caption=query.message.caption + "\n\n❌ پرداخت رد شد."
        )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN تنظیم نشده است.")

    app = Application.builder().token(BOT_TOKEN).build()

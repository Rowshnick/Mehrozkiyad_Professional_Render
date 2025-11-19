import os
import logging
from datetime import datetime
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)
from utils import astro, healing, sigil_local, text_ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LANG, NAME, GENDER, BDATE, BTIME, BPLACE, TARGET = range(7)

def build_app():
    token = os.getenv('TG_BOT_TOKEN')
    if not token:
        raise RuntimeError("TG_BOT_TOKEN not set in environment variables")
    return ApplicationBuilder().token(token).build()

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['فارسی', 'English']]
    await update.message.reply_text(
        "Please choose language / لطفاً زبان را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return LANG

async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled / لغو شد.")
    return ConversationHandler.END

def run_bot():
    app = build_app()

    async def lang_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.lower()
        context.user_data['lang'] = 'fa' if 'فار' in text else 'en'
        if context.user_data['lang'] == 'fa':
            await update.message.reply_text('خوش آمدید! لطفاً نام کوچک را وارد کنید.')
        else:
            await update.message.reply_text('Welcome! Please enter your first name.')
        return NAME

    async def name_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['name'] = update.message.text.strip()
        if context.user_data.get('lang') == 'fa':
            await update.message.reply_text('جنسیت را وارد کنید (یا بنویسید skip):')
        else:
            await update.message.reply_text('Enter gender (or type skip):')
        return GENDER

    async def gender_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
        txt = update.message.text.strip()
        context.user_data['gender'] = None if txt.lower() == 'skip' else txt
        if context.user_data.get('lang') == 'fa':
            await update.message.reply_text('تاریخ تولد (YYYY-MM-DD):')
        else:
            await update.message.reply_text('Birth date (YYYY-MM-DD):')
        return BDATE

    async def bdate_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
        txt = update.message.text.strip()
        try:
            bd = datetime.strptime(txt, '%Y-%m-%d')
            context.user_data['birth_date'] = bd
        except Exception:
            if context.user_data.get('lang') == 'fa':
                await update.message.reply_text('❌ فرمت تاریخ اشتباه است. مثال: 1992-05-21')
            else:
                await update.message.reply_text('❌ Invalid date format. Example: 1992-05-21')
            return BDATE

        if context.user_data.get('lang') == 'fa':
            await update.message.reply_text('ساعت تولد (HH:MM) یا skip:')
        else:
            await update.message.reply_text('Birth time (HH:MM) or skip:')
        return BTIME

    async def btime_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
        txt = update.message.text.strip()
        if txt.lower() == 'skip':
            context.user_data['birth_time'] = None
        else:
            try:
                context.user_data['birth_time'] = datetime.strptime(txt, '%H:%M')
            except Exception:
                if context.user_data.get('lang') == 'fa':
                    await update.message.reply_text('❌ فرمت ساعت اشتباه است. مثال: 14:30')
                else:
                    await update.message.reply_text('❌ Invalid time format. Example: 14:30')
                return BTIME

        if context.user_data.get('lang') == 'fa':
            await update.message.reply_text('محل تولد (یا skip):')
        else:
            await update.message.reply_text('Birth city (or skip):')
        return BPLACE

    async def bplace_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
        txt = update.message.text.strip()
        context.user_data['birth_place'] = None if txt.lower() == 'skip' else txt
        if context.user_data.get('lang') == 'fa':
            await update.message.reply_text('🎯 هدف شما؟ wealth / love / health / career')
        else:
            await update.message.reply_text('🎯 What is your goal? wealth / love / health / career')
        return TARGET

    async def target_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
        goal = update.message.text.strip().lower()
        name = context.user_data.get('name', 'User')

        bd = context.user_data.get('birth_date')
        bt = context.user_data.get('birth_time')

        if bd:
            if bt:
                birth_dt = datetime(bd.year, bd.month, bd.day, bt.hour, bt.minute)
            else:
                birth_dt = datetime(bd.year, bd.month, bd.day, 12, 0)
            chart = astro.compute_chart(birth_dt)
        else:
            chart = {'sun': 'Aries', 'moon': 'Cancer'}

        healing_data = healing.select(goal)
        summary = text_ai.generate_text(name, goal, chart)
        zodiac = chart.get('sun')
        sigil_file = sigil_local.generate_local(name, zodiac)

        lang = context.user_data.get('lang')

        if lang == 'fa':
            msg = (f"نتیجه برای {name}\\nخورشید: {zodiac}\\n"
                   f"سنگ‌ها: {', '.join([s.get('fa', s.get('en','')) for s in healing_data.get('stones',[])])}\\n"
                   f"گیاهان: {', '.join([h.get('fa', h.get('en','')) for h in healing_data.get('herbs',[])])}\\n\\n"
                   f"{summary.get('fa','')}")
        else:
            msg = (f"Result for {name}\\nSun: {zodiac}\\n"
                   f"Stones: {', '.join([s.get('en', s.get('fa','')) for s in healing_data.get('stones',[])])}\\n"
                   f"Herbs: {', '.join([h.get('en', h.get('fa','')) for h in healing_data.get('herbs',[])])}\\n\\n"
                   f"{summary.get('en','')}")
        await update.message.reply_text(msg)

        try:
            if sigil_file and os.path.exists(sigil_file):
                with open(sigil_file, 'rb') as f:
                    await update.message.reply_photo(f)
        except Exception as e:
            logger.error("Could not send sigil image: %s", e)

        return ConversationHandler.END

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start_cmd)],
        states={
            LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, lang_chosen)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_h)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_h)],
            BDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bdate_h)],
            BTIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, btime_h)],
            BPLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bplace_h)],
            TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, target_h)],
        },
        fallbacks=[CommandHandler('cancel', cancel_cmd)],
        allow_reentry=True
    )

    app.add_handler(conv)

    # webhook vs polling
    external = (os.getenv('RENDER_EXTERNAL_URL') or os.getenv('EXTERNAL_URL') or "").rstrip('/')
    token = os.getenv('TG_BOT_TOKEN')
    path = os.getenv('WEBHOOK_PATH') or (token.replace(':','_') if token else None)
    os.makedirs('outputs/sigils', exist_ok=True)

    if external and path:
        webhook_url = f"{external}/{path}"
        logger.info("Starting webhook mode. webhook_url=%s", webhook_url)
        try:
            app.run_webhook(
                listen='0.0.0.0',
                port=int(os.getenv('PORT', 10000)),
                url_path=path,
                webhook_url=webhook_url
            )
        except Exception:
            logger.exception("run_webhook failed")
            raise
    else:
        logger.info("Starting polling mode (no RENDER_EXTERNAL_URL found).")
        app.run_polling()

if __name__ == '__main__':
    run_bot()

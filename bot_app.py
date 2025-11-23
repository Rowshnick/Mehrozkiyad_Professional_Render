import os
import logging
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters, ConversationHandler
)
from persiantools.jdatetime import JalaliDate
from utils import astro, healing, sigil_local, text_ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- States ---
MENU, LANG, NAME, GENDER, BDATE, BTIME, BPLACE, TARGET = range(8)
DATE_MODE, YEAR, MONTH, DAY = range(8, 12)

def build_app():
    token = os.getenv('TG_BOT_TOKEN')
    if not token:
        raise RuntimeError("TG_BOT_TOKEN not set in environment variables")
    return ApplicationBuilder().token(token).build()

# --- منوی اصلی ---
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ثبت تولد", callback_data="birth"), 
         InlineKeyboardButton("تبدیل تاریخ", callback_data="date_convert")],
        [InlineKeyboardButton("لغو", callback_data="cancel")]
    ]
    # پاسخ متنی یا callback
    if update.message:
        await update.message.reply_text(
            "لطفاً یک گزینه انتخاب کنید:", 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "لطفاً یک گزینه انتخاب کنید:", 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    return MENU

# --- /start ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await main_menu(update, context)

# --- /cancel ---
async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لغو شد / Cancelled.")
    return ConversationHandler.END

# --- منوی اصلی callback ---
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "birth":
        keyboard = [
            [InlineKeyboardButton("فارسی", callback_data="fa"),
             InlineKeyboardButton("English", callback_data="en")]
        ]
        await query.message.reply_text(
            "لطفاً زبان را انتخاب کنید / Please choose language:", 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return LANG

    elif choice == "date_convert":
        keyboard = [
            [InlineKeyboardButton("میلادی → شمسی", callback_data="greg_to_jalali"),
             InlineKeyboardButton("شمسی → میلادی", callback_data="jalali_to_greg")],
            [InlineKeyboardButton("لغو", callback_data="cancel")]
        ]
        await query.message.reply_text(
            "لطفاً نوع تبدیل را انتخاب کنید:", 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return DATE_MODE

    elif choice == "cancel":
        return await cancel_cmd(update, context)

# --- انتخاب زبان ---
async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data
    context.user_data['lang'] = lang
    if lang == "fa":
        await query.message.reply_text("خوش آمدید! لطفاً نام کوچک را وارد کنید.")
    else:
        await query.message.reply_text("Welcome! Please enter your first name.")
    return NAME

# --- ثبت تولد handlers ---
async def name_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    lang = context.user_data.get('lang')
    msg = "جنسیت را وارد کنید (یا بنویسید skip):" if lang=='fa' else "Enter gender (or type skip):"
    await update.message.reply_text(msg)
    return GENDER

async def gender_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    context.user_data['gender'] = None if txt.lower() == 'skip' else txt
    lang = context.user_data.get('lang')
    msg = "تاریخ تولد (YYYY-MM-DD):" if lang=='fa' else "Birth date (YYYY-MM-DD):"
    await update.message.reply_text(msg)
    return BDATE

async def bdate_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    try:
        context.user_data['birth_date'] = datetime.strptime(txt, '%Y-%m-%d')
    except Exception:
        lang = context.user_data.get('lang')
        msg = '❌ فرمت تاریخ اشتباه است. مثال: 1992-05-21' if lang=='fa' else '❌ Invalid date format. Example: 1992-05-21'
        await update.message.reply_text(msg)
        return BDATE
    lang = context.user_data.get('lang')
    msg = 'ساعت تولد (HH:MM) یا skip:' if lang=='fa' else 'Birth time (HH:MM) or skip:'
    await update.message.reply_text(msg)
    return BTIME

async def btime_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if txt.lower() == 'skip':
        context.user_data['birth_time'] = None
    else:
        try:
            context.user_data['birth_time'] = datetime.strptime(txt, '%H:%M')
        except Exception:
            lang = context.user_data.get('lang')
            msg = '❌ فرمت ساعت اشتباه است. مثال: 14:30' if lang=='fa' else '❌ Invalid time format. Example: 14:30'
            await update.message.reply_text(msg)
            return BTIME
    lang = context.user_data.get('lang')
    msg = 'محل تولد (یا skip):' if lang=='fa' else 'Birth city (or skip):'
    await update.message.reply_text(msg)
    return BPLACE

async def bplace_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    context.user_data['birth_place'] = None if txt.lower() == 'skip' else txt
    lang = context.user_data.get('lang')
    msg = '🎯 هدف شما؟ wealth / love / health / career' if lang=='fa' else '🎯 What is your goal? wealth / love / health / career'
    await update.message.reply_text(msg)
    return TARGET

async def target_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.strip().lower()
    name = context.user_data.get('name', 'User')
    bd = context.user_data.get('birth_date')
    bt = context.user_data.get('birth_time')
    if bd:
        birth_dt = datetime(bd.year, bd.month, bd.day, bt.hour if bt else 12, bt.minute if bt else 0)
        chart = astro.compute_chart(birth_dt)
    else:
        chart = {'sun': 'Aries', 'moon': 'Cancer'}
    healing_data = healing.select(goal)
    summary = text_ai.generate_text(name, goal, chart)
    zodiac = chart.get('sun')
    sigil_file = sigil_local.generate_local(name, zodiac)
    lang = context.user_data.get('lang')
    if lang == 'fa':
        msg = (f"نتیجه برای {name}\nخورشید: {zodiac}\n"
               f"سنگ‌ها: {', '.join([s.get('fa', s.get('en','')) for s in healing_data.get('stones',[])])}\n"
               f"گیاهان: {', '.join([h.get('fa', h.get('en','')) for h in healing_data.get('herbs',[])])}\n\n"
               f"{summary.get('fa','')}")
    else:
        msg = (f"Result for {name}\nSun: {zodiac}\n"
               f"Stones: {', '.join([s.get('en', s.get('fa','')) for s in healing_data.get('stones',[])])}\n"
               f"Herbs: {', '.join([h.get('en', h.get('fa','')) for h in healing_data.get('herbs',[])])}\n\n"
               f"{summary.get('en','')}")
    await update.message.reply_text(msg)
    try:
        if sigil_file and os.path.exists(sigil_file):
            with open(sigil_file, 'rb') as f:
                await update.message.reply_photo(f)
    except Exception as e:
        logger.error("Could not send sigil image: %s", e)
    return await main_menu(update, context)

# --- تبدیل تاریخ handlers ---
async def date_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    if choice == 'cancel':
        return await cancel_cmd(update, context)
    context.user_data['date_mode'] = choice
    await query.message.reply_text("سال را وارد کنید:")
    return YEAR

async def year_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['year'] = int(update.message.text.strip())
    await update.message.reply_text("ماه را وارد کنید:")
    return MONTH

async def month_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['month'] = int(update.message.text.strip())
    await update.message.reply_text("روز را وارد کنید:")
    return DAY

async def day_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = int(update.message.text.strip())
    year = context.user_data['year']
    month = context.user_data['month']
    mode = context.user_data['date_mode']
    try:
        if mode == 'greg_to_jalali':
            dt = datetime(year, month, day)
            jd = JalaliDate(dt)
            await update.message.reply_text(f"تاریخ شمسی: {jd.year}-{jd.month:02d}-{jd.day:02d}")
        else:
            jd = JalaliDate(year, month, day)
            gd = jd.to_gregorian()
            await update.message.reply_text(f"تاریخ میلادی: {gd.year}-{gd.month:02d}-{gd.day:02d}")
    except Exception:
        await update.message.reply_text("❌ تاریخ نامعتبر است")
    return await main_menu(update, context)

# --- RUN BOT ---
def run_bot():
    app = build_app()
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start_cmd)],
        states={
            MENU: [CallbackQueryHandler(menu_callback)],
            LANG: [CallbackQueryHandler(lang_callback)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_h)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_h)],
            BDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bdate_h)],
            BTIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, btime_h)],
            BPLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bplace_h)],
            TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, target_h)],
            DATE_MODE: [CallbackQueryHandler(date_mode_callback)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, year_h)],
            MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, month_h)],
            DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, day_h)],
        },
        fallbacks=[CommandHandler('cancel', cancel_cmd)],
        allow_reentry=True
    )
    app.add_handler(conv)

    external = (os.getenv('RENDER_EXTERNAL_URL') or os.getenv('EXTERNAL_URL') or "").rstrip('/')
    path = "mehrozkiyad_webhook"
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('outputs/sigils', exist_ok=True)

    if external:
        webhook_url = f"{external}/{path}"
        logger.info("Starting webhook mode. webhook_url=%s", webhook_url)
        app.run_webhook(
            listen='0.0.0.0',
            port=int(os.getenv('PORT', 10000)),
            url_path=path,
            webhook_url=webhook_url
        )
    else:
        logger.info("Starting polling mode (no external URL).")
        app.run_polling()

if __name__ == '__main__':
    run_bot()

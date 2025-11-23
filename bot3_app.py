import os
import datetime
import swisseph as swe
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, filters
from persiantools.jdatetime import JalaliDate
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
print("TOKEN:", TOKEN)

# مراحل conversation
LANG, DATE_YEAR, DATE_MONTH, DATE_DAY, SIGN, FORECAST = range(6)

# زودیاک و نمادها
ZODIAC = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
ZODIAC_FA = ['حمل','ثور','جوزا','سرطان','اسد','سنبله','میزان','عقرب','قوس','جدی','دلو','حوت']
SYMS = {'Aries':'♈','Taurus':'♉','Gemini':'♊','Cancer':'♋','Leo':'♌','Virgo':'♍','Libra':'♎','Scorpio':'♏','Sagittarius':'♐','Capricorn':'♑','Aquarius':'♒','Pisces':'♓'}
LUCKY_SIGILS = ['☀️','🌙','⭐','🪐','🔯']

# تابع تولید تصویر
def generate_image(name, zodiac, out_path=None):
    os.makedirs('outputs/sigils', exist_ok=True)
    safe_name = ''.join(c for c in name if c.isalnum() or c in (' ','_')).strip().replace(' ','_')
    if out_path is None:
        out_path = f"outputs/sigils/{safe_name}_{zodiac}.png"
    img = Image.new('RGB',(800,800),(18,24,44))
    draw = ImageDraw.Draw(img)
    sym = SYMS.get(zodiac,'?')
    FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    font = ImageFont.truetype(FONT,160)
    w,h = draw.textsize(sym,font=font)
    draw.text(((800-w)/2,120), sym, font=font, fill=(245,220,130))
    f2 = ImageFont.truetype(FONT,28)
    w,h = draw.textsize(name,font=f2)
    draw.text(((800-w)/2,700), name, font=f2, fill=(230,230,230))
    img.save(out_path)
    return out_path

# محاسبه موقعیت سیارات
def calculate_planets(year, month, day):
    jd = swe.julday(year, month, day)
    planets = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
    positions = {}
    for i, p in enumerate(planets):
        lon, lat, dist = swe.calc_ut(jd, i)[0:3]
        positions[p] = lon
    return positions

# تولید پیشگویی طولانی
def generate_forecast(name, zodiac, positions, lang='fa'):
    if lang=='fa':
        forecast = f"سلام {name}! 🌟\nبر اساس وضعیت ستارگان امروز برای {zodiac}:\n"
        for p, lon in positions.items():
            forecast += f"- {p}: {lon:.2f}°\n"
        forecast += "\nامروز روز مناسبی برای تمرکز روی عشق و روابط شماست. 🌙\n"
        forecast += "در زمینه شغل و درآمد، فرصت‌های تازه ممکن است ظاهر شوند.\n"
        forecast += "سلامتی خود را با فعالیت‌های سبک و مراقبت از خود تقویت کنید.\n"
        forecast += "پیشنهاد: نماد خوش‌یمن شما امروز " + LUCKY_SIGILS[hash(name)%len(LUCKY_SIGILS)] + " است."
    else:
        forecast = f"Hello {name}! 🌟\nBased on today's stars for {zodiac}:\n"
        for p, lon in positions.items():
            forecast += f"- {p}: {lon:.2f}°\n"
        forecast += "\nToday is good for focusing on love and relationships. 🌙\n"
        forecast += "Career and wealth opportunities may appear.\n"
        forecast += "Maintain your health with light exercise and self-care.\n"
        forecast += "Suggestion: Your lucky symbol today is " + LUCKY_SIGILS[hash(name)%len(LUCKY_SIGILS)] + "."
    return forecast

# Handler شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("فارسی", callback_data='fa')],
                [InlineKeyboardButton("English", callback_data='en')]]
    await update.message.reply_text("لطفا زبان خود را انتخاب کنید:" ,reply_markup=InlineKeyboardMarkup(keyboard))
    return LANG

# انتخاب زبان
async def lang_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data
    context.user_data['lang'] = lang
    if lang=='fa':
        years = [str(y) for y in range(1300, 1410)]
        text = "سال تولد خود را انتخاب کنید:"
    else:
        years = [str(y) for y in range(1920, 2030)]
        text = "Select your birth year:"
    keyboard = [[InlineKeyboardButton(y, callback_data=y) for y in years[i:i+4]] for i in range(0,len(years),4)]
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    return DATE_YEAR

# ادامه مراحل برای ماه، روز و علامت زودیاک مشابه همین متد

# Main
app = ApplicationBuilder().token(TOKEN).build()
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        LANG: [CallbackQueryHandler(lang_choice)],
        # ادامه: DATE_YEAR, DATE_MONTH, DATE_DAY, SIGN, FORECAST
    },
    fallbacks=[]
)
app.add_handler(conv_handler)
app.run_polling()

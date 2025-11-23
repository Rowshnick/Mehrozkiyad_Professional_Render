import os import datetime import swisseph as swe from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler

--- Constants and Globals ---

LANG, DAY, MONTH, YEAR = range(4) SYMS = {'Aries':'♈','Taurus':'♉','Gemini':'♊','Cancer':'♋','Leo':'♌','Virgo':'♍','Libra':'♎','Scorpio':'♏','Sagittarius':'♐','Capricorn':'♑','Aquarius':'♒','Pisces':'♓'} LANGUAGES = {'English':'en','فارسی':'fa'}

--- Helper Functions ---

def generate_astrology_prediction(year, month, day, language='en'): jd = swe.julday(year, month, day) planets = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto'] positions = {} for i, p in enumerate([swe.SUN,swe.MOON,swe.MERCURY,swe.VENUS,swe.MARS,swe.JUPITER,swe.SATURN,swe.URANUS,swe.NEPTUNE,swe.PLUTO]): lon, lat, dist = swe.calc_ut(jd, p)[:3] positions[planets[i]] = lon

# Example house calculation (Ascendant)
asc = swe.houses(jd, 0, 0)[0][0]  # Simplified, lat/lon=0

# Generate long prediction text
text = f"Planetary positions on {year}-{month}-{day}:\n"
for pl, pos in positions.items():
    text += f"{pl}: {pos:.2f}°\n"
text += f"Ascendant: {asc:.2f}°\n\n"
text += "Based on these positions, today is favorable for focusing on personal growth, relationships, and career advancements.\n"
text += "Recommendations: choose your lucky stone, plant, and symbol to harmonize your energy."
return text

def generate_lucky_items(): return {'stone':'Amethyst','plant':'Lavender','symbol':'☯'}

--- Telegram Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): buttons = [[InlineKeyboardButton(l, callback_data=l)] for l in LANGUAGES.keys()] keyboard = InlineKeyboardMarkup(buttons) await update.message.reply_text('Choose your language / زبان خود را انتخاب کنید:', reply_markup=keyboard) return LANG

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() lang = query.data context.user_data['lang'] = LANGUAGES[lang] # Ask for year year_buttons = [[InlineKeyboardButton(str(y), callback_data=str(y))] for y in range(1980, 2010)] await query.message.reply_text('Select your birth year / سال تولد خود را انتخاب کنید:', reply_markup=InlineKeyboardMarkup(year_buttons)) return YEAR

async def choose_year(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() context.user_data['year'] = int(query.data) # Ask for month month_buttons = [[InlineKeyboardButton(str(m), callback_data=str(m))] for m in range(1,13)] await query.message.reply_text('Select your birth month / ماه تولد خود را انتخاب کنید:', reply_markup=InlineKeyboardMarkup(month_buttons)) return MONTH

async def choose_month(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() context.user_data['month'] = int(query.data) # Ask for day day_buttons = [[InlineKeyboardButton(str(d), callback_data=str(d))] for d in range(1,32)] await query.message.reply_text('Select your birth day / روز تولد خود را انتخاب کنید:', reply_markup=InlineKeyboardMarkup(day_buttons)) return DAY

async def choose_day(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() context.user_data['day'] = int(query.data) # Generate prediction year = context.user_data['year'] month = context.user_data['month'] day = context.user_data['day'] lang = context.user_data['lang'] prediction = generate_astrology_prediction(year, month, day, lang) items = generate_lucky_items() final_text = f"{prediction}\n\nLucky stone: {items['stone']}, Plant: {items['plant']}, Symbol: {items['symbol']}" await query.message.reply_text(final_text) return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text('Operation cancelled.') return ConversationHandler.END

--- Main ---

app = ApplicationBuilder().token(os.getenv('BOT_TOKEN')).build() conv_handler = ConversationHandler( entry_points=[CommandHandler('start', start)], states={ LANG: [CallbackQueryHandler(choose_language)], YEAR: [CallbackQueryHandler(choose_year)], MONTH: [CallbackQueryHandler(choose_month)], DAY: [CallbackQueryHandler(choose_day)], }, fallbacks=[CommandHandler('cancel', cancel)] ) app.add_handler(conv_handler)

if name == 'main': print('Bot started...') app.run_polling()

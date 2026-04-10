import requests
import re
from deep_translator import GoogleTranslator
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

print("🔥 SMART MOVIE BOT STARTED")

# 🔑 ОСЫ ЖЕРГЕ ӨЗІҢНІҢ КЛЮЧТЕРІН ҚОЙ
TOKEN = "8753096730:AAESqV0zjvgWuguQ2wDgiA-r1dCjFoFhi9Q"
OMDB_API = "fc5f225a"

keyboard = [["🎬 Кино"]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

user_mode = {}

# 🔥 ҚОЛМЕН АУДАРУ (popular movies)
def smart_translate(text):
    text = text.lower()

    if "паук" in text or "өрмекші" in text:
        return "spider man"
    if "гарри поттер" in text:
        return "harry potter"
    if "мстители" in text:
        return "avengers"
    if "интерстеллар" in text:
        return "interstellar"

    return text

# 🌐 АУДАРМА
def translate_to_en(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text

def translate_to_kz(text):
    try:
        return GoogleTranslator(source='auto', target='kk').translate(text)
    except:
        return text

# 🎬 ІЗДЕУ
def search_movies(title):
    url = f"https://www.omdbapi.com/?s={title}&apikey={OMDB_API}"
    return requests.get(url).json()

# 🎬 ДЕТАЛЬ
def get_movie(imdb_id):
    url = f"https://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API}"
    return requests.get(url).json()

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_mode[update.effective_user.id] = "movie"
    await update.message.reply_text(
        "🎬 Smart Movie Bot 😎\nКино атын жаз (қазақша / орысша / ағылшынша):",
        reply_markup=markup
    )

# 💬 MESSAGE
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # 🎬 КНОПКА
    if text == "🎬 Кино":
        user_mode[user_id] = "movie"
        await update.message.reply_text("🎬 Кино атын жаз:")
        return

    # 🎬 ІЗДЕУ
    if user_mode.get(user_id) == "movie":

        # 🔥 ЖЫЛ АЛУ
        year_match = re.search(r"(19|20)\d{2}", text)
        year = year_match.group() if year_match else None

        clean_text = re.sub(r"\d+", "", text)

        translated = smart_translate(clean_text)
        translated = translate_to_en(translated)

        data = search_movies(translated)

        if data.get("Response") == "True":

            movies = data["Search"]

            # 🔥 ЖЫЛ ФИЛЬТР
            if year:
                movies = [m for m in movies if m["Year"] == year]

            if not movies:
                await update.message.reply_text("❌ Сол жылдағы кино табылмады")
                return

            buttons = []

            for m in movies[:8]:  # максимум 8 фильм
                buttons.append([
                    InlineKeyboardButton(
                        f"{m['Title']} ({m['Year']})",
                        callback_data=m["imdbID"]
                    )
                ])

            await update.message.reply_text(
                "🎬 Таңда👇",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        else:
            await update.message.reply_text("❌ Табылмады 😢")

# 🎬 ТАҢДАЛҒАН КИНО
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    imdb_id = query.data
    movie = get_movie(imdb_id)

    if movie.get("Response") == "True":

        title = movie["Title"]
        year = movie["Year"]
        rating = movie["imdbRating"]
        plot = movie["Plot"]
        poster = movie["Poster"]

        # 🔥 ҚАЗАҚША АУДАРУ
        plot_kz = translate_to_kz(plot)

        # 🔥 КИНО САЙТ ССЫЛКА
        url = f"https://www.google.com/search?q={title}+смотреть+онлайн"

        keyboard_inline = [
            [InlineKeyboardButton("🎬 Кино көру", url=url)]
        ]

        await query.message.reply_photo(
            photo=poster,
            caption=f"🎬 {title} ({year})\n⭐ {rating}\n\n📖 {plot_kz}",
            reply_markup=InlineKeyboardMarkup(keyboard_inline)
        )

# 🚀 RUN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.add_handler(CallbackQueryHandler(handle_callback))

app.run_polling()
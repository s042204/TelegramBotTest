import logging
import requests
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define a thread pool executor
executor = ThreadPoolExecutor(max_workers=3)

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hello, {user.mention_html()}! Welcome to the Multithreaded Telegram Bot.",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Help! How can I assist you?')

# Define a background task for a long-running operation
def background_task(name: str) -> str:
    import time
    time.sleep(5)  # Simulate a long-running task
    return f'Task {name} completed!'

# Define a command to start the background task
async def start_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    task_name = 'Task1'
    await update.message.reply_text(f'Starting {task_name}...')

    loop = asyncio.get_event_loop()
    future_result = loop.run_in_executor(executor, background_task, task_name)
    result = await future_result

    await update.message.reply_text(result)

# Define a background task for fetching a joke 
def fetch_joke() -> str:
    response = requests.get('https://official-joke-api.appspot.com/random_joke')
    joke = response.json()
    return f'{joke["setup"]} - {joke["punchline"]}'

# Define a command to fetch a joke
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Fetching a joke...')

    loop = asyncio.get_event_loop()
    future_result = loop.run_in_executor(executor, fetch_joke)
    result = await future_result

    await update.message.reply_text(result)

# Define a background task for fetching weather data
def fetch_weather(city: str) -> str:
    api_key = "YOUR_OPENWEATHERMAP_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data["cod"] != 200:
        return "City not found."

    weather_description = data["weather"][0]["description"]
    temperature = data["main"]["temp"]
    return f"The weather in {city} is {weather_description} with a temperature of {temperature}°C."

# Define a command to fetch weather
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city = " ".join(context.args)
    if not city:
        await update.message.reply_text("Please provide a city name.")
        return

    await update.message.reply_text(f"Fetching weather for {city}...")

    loop = asyncio.get_event_loop()
    future_result = loop.run_in_executor(executor, fetch_weather, city)
    result = await future_result

    await update.message.reply_text(result)

def main() -> None:
    application = Application.builder().token("7424786482:AAHS4UlJHWs4877l8vwTLn30UoaS58bQBik").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start_task", start_task))
    application.add_handler(CommandHandler("joke", joke))
    application.add_handler(CommandHandler("weather", weather))

    application.run_polling()

if __name__ == '__main__':
    main()
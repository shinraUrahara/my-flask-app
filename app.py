import fitz  # PyMuPDF
from PIL import Image
from telegram import Bot
from telegram.ext import ApplicationBuilder
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
import os
from flask import Flask
from threading import Thread

# === CONFIGURATION ===
PDF_PATH = "quran.pdf"
BOT_TOKEN = "7587937849:AAGxK5Zow4LP01gKcgoa_cnxnW2SUFXGO8I"  # 🔁 Replace with your BotFather token
YOUR_TELEGRAM_USER_ID = 6931130756       # 🔁 Replace with your Telegram user ID
PAGE_STATE_FILE = "page_state.txt"

# === WEB SERVER FOR UPTIMEROBOT ===
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    web_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run_web).start()

# === PDF TO PNG ===
def convert_pdf_to_png(pdf_path, page_start=0, num_pages=2):
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(page_start, min(page_start + num_pages, len(doc))):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=150)
        image_path = f"page_{page_num + 1}.png"
        pix.save(image_path)
        image_paths.append(image_path)

    return image_paths

# === TRACK PAGE PROGRESS ===
def get_current_page():
    if not os.path.exists(PAGE_STATE_FILE):
        return 0
    with open(PAGE_STATE_FILE, "r") as f:
        return int(f.read().strip())

def save_current_page(page):
    with open(PAGE_STATE_FILE, "w") as f:
        f.write(str(page))

# === SEND IMAGES ===
async def send_pdf_pages():
    current_page = get_current_page()
    image_paths = convert_pdf_to_png(PDF_PATH, current_page, 2)

    bot = Bot(token=BOT_TOKEN)
    for path in image_paths:
        with open(path, 'rb') as img:
            await bot.send_photo(chat_id=YOUR_TELEGRAM_USER_ID, photo=img)

    # Clean up and update page
    for path in image_paths:
        os.remove(path)

    save_current_page(current_page + 2)

# === DAILY SCHEDULER ===
def schedule_daily_task(app):
    kuwait_tz = pytz.timezone("Asia/Kuwait")
    scheduler = BackgroundScheduler(timezone=kuwait_tz)
    scheduler.add_job(lambda: app.create_task(send_pdf_pages()), trigger='cron', hour=4, minute=0)
    scheduler.start()

# === MAIN ===
if __name__ == "__main__":
    keep_alive()  # Start web server
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    schedule_daily_task(app)

    print("Bot is running and scheduled for 4AM Kuwait time...")
    app.run_polling()

import os
from flask import Flask

app = Flask(__name__)

# Your routes and app logic here

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


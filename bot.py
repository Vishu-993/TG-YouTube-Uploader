import os
import asyncio
import yt_dlp
from urllib.parse import urlparse
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_dl import YoutubeDL
from opencc import OpenCC
from config import Config
import wget
from pyrogram.enums import ParseMode
import time
import pickle
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

CHROMEDRIVER_PATH = "./chromedriver"  # Update if needed

def generate_terabox_session():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://terabox.com/login")
        time.sleep(5)  # Wait for page to load

        # Find and download QR code
        qr_element = driver.find_element(By.XPATH, "//img[contains(@src, 'qrcode')]")
        qr_url = qr_element.get_attribute("src")

        qr_path = "terabox_qr.png"
        response = requests.get(qr_url)
        with open(qr_path, "wb") as file:
            file.write(response.content)

        print("QR Code saved as", qr_path)

        # Wait for the user to scan
        time.sleep(20)  # Adjust time if needed

        # Extract session cookies
        cookies = driver.get_cookies()
        with open("terabox_session.pkl", "wb") as file:
            pickle.dump(cookies, file)

        print("Session saved successfully!")
        return qr_path, "terabox_session.pkl"

    finally:
        driver.quit()



Jebot = Client(
   "YT Downloader",
   api_id=Config.APP_ID,
   api_hash=Config.API_HASH,
   bot_token=Config.TG_BOT_TOKEN,
)

YTDL_REGEX = (r"^((?:https?:)?\/\/)"
              r"?((?:www|m)\.)"
              r"?((?:youtube\.com|youtu\.be|xvideos\.com|pornhub\.com"
              r"|xhamster\.com|xnxx\.com))"
              r"(\/)([-a-zA-Z0-9()@:%_\+.~#?&//=]*)([\w\-]+)(\S+)?$")
s2tw = OpenCC('s2tw.json').convert


@Jebot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Welcome! Use /generate to create a Terabox session.")

@Jebot.on_message(filters.command("generate"))
async def generate_session(client, message):
    await message.reply("Generating QR Code... Please wait and get ready with two mobiles.")

    qr_path, session_path = generate_terabox_session()

    if os.path.exists(qr_path):
        await client.send_photo(message.chat.id, qr_path, caption="Scan this QR Code with your Terabox app.")
        os.remove(qr_path)

        if os.path.exists(session_path):
            await message.reply_document(session_path, caption="✅ Login Successful! Here's your session file.")
            os.remove(session_path)
        else:
            await message.reply("⚠️ Login failed. Please try again.")
    else:
        await message.reply("❌ Failed to generate QR Code.")



@Jebot.on_message(filters.command("start"))
async def start(client, message):
    await client.send_message(
        chat_id=message.chat.id,
        text="""<b>Hello! This is a YouTube Uploader Bot

I can download video or audio from Youtube. Made by @TheTeleRoid 🇮🇳

Hit help button to find out more about how to use me</b>""",   
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("⭕ Channel ⭕", url="https://t.me/TeleRoidGroup"),
                InlineKeyboardButton("🛑 Support 🛑", url="https://t.me/TeleRoid14")
            ],[
                InlineKeyboardButton("Source Code", url="https://github.com/P-Phreak/TG-YouTube-Uploader")
            ]]
        ),        
        disable_web_page_preview=True,        
        parse_mode=ParseMode.HTML
    )


@Jebot.on_message(filters.command("help"))
async def help(client, message):
    await client.send_message(
        chat_id=message.chat.id,
        text="""<b>YouTube Bot Help!

Just send a Youtube URL to download it in video or audio format!

~ @TeleRoidGroup</b>""",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("⭕ Channel ⭕", url="https://t.me/TeleRoidGroup"),
                InlineKeyboardButton("🛑 Support 🛑", url="https://t.me/TeleRoid14"),
            ],[
                InlineKeyboardButton("About Meh👤", url="https://t.me/TheTeleRoid")
            ]]
        ),        
        disable_web_page_preview=True,        
        parse_mode=ParseMode.HTML
    )


@Jebot.on_message(filters.command("about"))
async def about(client, message):
    await client.send_message(
        chat_id=message.chat.id,
        text="""<b>About TeleRoid YouTube Bot!</b>

<b>👨‍💻 Developer:</b> <a href="https://t.me/PredatorHackerzZ_bot">Predator 🇮🇳</a>

<b>💁‍♂️ Support:</b> <a href="https://t.me/TeleRoid14">TeleRoid Support</a>

<b>😇 Channel :</b> <a href="https://t.me/TeleRoidGroup">TeleRoid Updates </a>

<b>📚 Library:</b> <a href="https://github.com/pyrogram/pyrogram">Pyrogram</a>

<b>🤖 BotList :</b> <a href="https://t.me/TGRobot_List"> Telegram Bots </a>

<b>📌 Source : </b> <a href="https://GitHub.com/P-Phreak/TG-YouTube-Uploader"> Click Here </a>

<b>~ @TeleRoidGroup</b>""",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("⭕ Join Our Channel ⭕", url="https://t.me/TeleRoidGroup"),
            ]]
        ),        
        disable_web_page_preview=True,        
        parse_mode=ParseMode.HTML
    )


# Handle video and audio download requests
@Jebot.on_message(filters.regex(YTDL_REGEX) & filters.private)
async def download_video(client, message):
    url = message.text
    await message.reply_text("⏳ Processing the video, please wait...")

    try:
        with YoutubeDL({'format': 'bestvideo+bestaudio/best'}) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
        
        # Sending the video
        caption = f"🎥 {s2tw(info_dict['title'])}\n🔗 [Source]({info_dict['webpage_url']})"
        await client.send_video(
            chat_id=message.chat.id,
            video=file_path,
            caption=caption,
            duration=int(info_dict['duration']),
            parse_mode=ParseMode.HTML
        )
        os.remove(file_path)

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")


   

# https://docs.pyrogram.org/start/examples/bot_keyboards
# Reply with inline keyboard
@Jebot.on_message(filters.private
                   & filters.text
                   & filters.regex(YTDL_REGEX))
async def ytdl_with_button(_, message: Message):
    await message.reply_text(
        "**Choose download type👇**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Audio 🎵",
                        callback_data="ytdl_audio"
                    ),
                    InlineKeyboardButton(
                        "Video 🎬",
                        callback_data="ytdl_video"
                    )
                ]
            ]
        ),
        quote=True
    )


@Jebot.on_callback_query(filters.regex("^ytdl_audio$"))
async def callback_query_ytdl_audio(_, callback_query):
    try:
        url = callback_query.message.reply_to_message.text
        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': '%(title)s - %(extractor)s-%(id)s.%(ext)s',
            'writethumbnail': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            message = callback_query.message
            await message.reply_chat_action("typing")
            info_dict = ydl.extract_info(url, download=False)
            # download
            await callback_query.edit_message_text("**Downloading audio...**")
            ydl.process_info(info_dict)
            # upload
            audio_file = ydl.prepare_filename(info_dict)
            task = asyncio.create_task(send_audio(message, info_dict,
                                                  audio_file))
            while not task.done():
                await asyncio.sleep(3)
                await message.reply_chat_action("upload_document")
            await message.reply_chat_action("cancel")
            await message.delete()
    except Exception as e:
        await message.reply_text(e)
    await callback_query.message.reply_to_message.delete()
    await callback_query.message.delete()


if Config.AUDIO_THUMBNAIL == "No":
   async def send_audio(message: Message, info_dict, audio_file):
       basename = audio_file.rsplit(".", 1)[-2]
       # .webm -> .weba
       if info_dict['ext'] == 'webm':
           audio_file_weba = basename + ".weba"
           os.rename(audio_file, audio_file_weba)
           audio_file = audio_file_weba
       # thumbnail
       thumbnail_url = info_dict['thumbnail']
       thumbnail_file = basename + "." + \
           get_file_extension_from_url(thumbnail_url)
       # info (s2tw)
       webpage_url = info_dict['webpage_url']
       title = s2tw(info_dict['title'])
       caption = f"<b><a href=\"{webpage_url}\">{title}</a></b>"
       duration = int(float(info_dict['duration']))
       performer = s2tw(info_dict['uploader'])
       await message.reply_audio(audio_file, caption=caption, duration=duration,
                              performer=performer, title=title,
                              parse_mode='HTML', thumb=thumbnail_file)
       os.remove(audio_file)
       os.remove(thumbnail_file)

else:
    async def send_audio(message: Message, info_dict, audio_file):
       basename = audio_file.rsplit(".", 1)[-2]
       # .webm -> .weba
       if info_dict['ext'] == 'webm':
           audio_file_weba = basename + ".weba"
           os.rename(audio_file, audio_file_weba)
           audio_file = audio_file_weba
       # thumbnail
       lol = Config.AUDIO_THUMBNAIL
       thumbnail_file = wget.download(lol)
       # info (s2tw)
       webpage_url = info_dict['webpage_url']
       title = s2tw(info_dict['title'])
       caption = f"<b><a href=\"{webpage_url}\">{title}</a></b>"
       duration = int(float(info_dict['duration']))
       performer = s2tw(info_dict['uploader'])
       await message.reply_audio(audio_file, caption=caption, duration=duration,
                              performer=performer, title=title,
                              parse_mode='HTML', thumb=thumbnail_file)
       os.remove(audio_file)
       os.remove(thumbnail_file)

@Jebot.on_callback_query(filters.regex("^ytdl_video$"))
async def callback_query_ytdl_video(_, callback_query):
    try:
        # url = callback_query.message.text
        url = callback_query.message.reply_to_message.text
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': '%(title)s - %(extractor)s-%(id)s.%(ext)s',
            'writethumbnail': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            message = callback_query.message
            await message.reply_chat_action("typing")
            info_dict = ydl.extract_info(url, download=False)
            # download
            await callback_query.edit_message_text("**Downloading video...**")
            ydl.process_info(info_dict)
            # upload
            video_file = ydl.prepare_filename(info_dict)
            task = asyncio.create_task(send_video(message, info_dict,
                                                  video_file))
            while not task.done():
                await asyncio.sleep(3)
                await message.reply_chat_action("upload_document")
            await message.reply_chat_action("cancel")
            await message.delete()
    except Exception as e:
        await message.reply_text(e)
    await callback_query.message.reply_to_message.delete()
    await callback_query.message.delete()

if Config.VIDEO_THUMBNAIL == "No":
   async def send_video(message: Message, info_dict, video_file):
      basename = video_file.rsplit(".", 1)[-2]
      # thumbnail
      thumbnail_url = info_dict['thumbnail']
      thumbnail_file = basename + "." + \
          get_file_extension_from_url(thumbnail_url)
      # info (s2tw)
      webpage_url = info_dict['webpage_url']
      title = s2tw(info_dict['title'])
      caption = f"<b><a href=\"{webpage_url}\">{title}</a></b>"
      duration = int(float(info_dict['duration']))
      width, height = get_resolution(info_dict)
      await message.reply_video(
          video_file, caption=caption, duration=duration,
          width=width, height=height, parse_mode='HTML',
          thumb=thumbnail_file)

      os.remove(video_file)
      os.remove(thumbnail_file)

else:
   async def send_video(message: Message, info_dict, video_file):
      basename = video_file.rsplit(".", 1)[-2]
      # thumbnail
      lel = Config.VIDEO_THUMBNAIL
      thumbnail_file = wget.download(lel)
      # info (s2tw)
      webpage_url = info_dict['webpage_url']
      title = s2tw(info_dict['title'])
      caption = f"<b><a href=\"{webpage_url}\">{title}</a></b>"
      duration = int(float(info_dict['duration']))
      width, height = get_resolution(info_dict)
      await message.reply_video(
          video_file, caption=caption, duration=duration,
          width=width, height=height, parse_mode='HTML',
          thumb=thumbnail_file)

      os.remove(video_file)
      os.remove(thumbnail_file)

def get_file_extension_from_url(url):
    url_path = urlparse(url).path
    basename = os.path.basename(url_path)
    return basename.split(".")[-1]


def get_resolution(info_dict):
    if {"width", "height"} <= info_dict.keys():
        width = int(info_dict['width'])
        height = int(info_dict['height'])
    # https://support.google.com/youtube/answer/6375112
    elif info_dict['height'] == 1080:
        width = 1920
        height = 1080
    elif info_dict['height'] == 720:
        width = 1280
        height = 720
    elif info_dict['height'] == 480:
        width = 854
        height = 480
    elif info_dict['height'] == 360:
        width = 640
        height = 360
    elif info_dict['height'] == 240:
        width = 426
        height = 240
    return (width, height)


@Jebot.on_callback_query()
async def button(bot, update):
      cb_data = update.data
      if "help" in cb_data:
        await update.message.delete()
        await help(bot, update.message)
      elif "about" in cb_data:
        await update.message.delete()
        await about(bot, update.message)
      elif "start" in cb_data:
        await update.message.delete()
        await start(bot, update.message)

print(
    """
Bot Started!
Join **@TGRobot_List**
"""
)

Jebot.run()

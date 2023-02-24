import os
from pytube import YouTube
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.utils import executor
import moviepy.editor as mp

API_TOKEN = 'Your_Token'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def process_video(video_url, chat_id, resolution):
    try:
        await bot.send_chat_action(chat_id, 'typing')
        yt = YouTube(video_url)
        if resolution == "audio":
            video = yt.streams.filter(only_audio=True).first()
            try:
                video_path = video.download()
                audio_path = os.path.splitext(video_path)[0] + '.mp3'
                clip = mp.AudioFileClip(video_path)
                clip.write_audiofile(audio_path)
                await bot.send_audio(chat_id, open(audio_path,'rb'))
                os.remove(audio_path)
                os.remove(video_path)
            except Exception as e:
                print(e)
                await bot.send_message(chat_id, "There is an error. Try again.")
        else:
            video = yt.streams.filter(progressive=True, file_extension='mp4', res=resolution).order_by('resolution').desc().first()
            filename = f'{yt.title}.mp4'
            video.download(output_path='./', filename=filename)
            await bot.send_video(chat_id, video=InputFile(filename), supports_streaming=True)
            os.remove(filename)
    except Exception as e:
        await bot.send_message(chat_id, f"An error occurred while sending the video: {e}")

async def process_resolution(callback_query: types.CallbackQuery):
    resolution = callback_query.data
    video_url = callback_query.message.reply_to_message.text
    chat_id = callback_query.message.chat.id
    await process_video(video_url, chat_id, resolution)
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nJust send me the YouTube video link")

@dp.message_handler(regexp='youtube.com|youtu.be/')
async def process_youtube_url(message: types.Message):
    video_url = message.text.strip()
    chat_id = message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="360p", callback_data="360p"),types.InlineKeyboardButton(text="720p", callback_data="720p"),types.InlineKeyboardButton(text="audio", callback_data="audio"))
    await bot.send_message(chat_id, "Choose video resolution:\n360 - for phone screen", reply_markup=keyboard, reply_to_message_id=message.message_id)

@dp.callback_query_handler(lambda c: c.data and c.data in ["360p", "720p", "audio"])
async def process_callback_resolution(callback_query: types.CallbackQuery):
    await process_resolution(callback_query)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
import yt_dlp
import os

# Получаем абсолютный путь к текущей папке проекта
current_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(current_dir, 'ffmpeg.exe')

ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    # Явно указываем yt-dlp, где искать исполняемый файл ffmpeg
    'ffmpeg_location': ffmpeg_path, 
    'socket_timeout': 60,
}

link = input("Введите ссылку для скачивания: ")

with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Тут тоже через подчеркивание
    ydl.download([link])
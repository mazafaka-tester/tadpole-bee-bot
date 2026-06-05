from flask import Flask, request, render_template # Импортируем request
import yt_dlp

app = Flask(__name__)

ydl_opts = {
    'outtmpl': '%(title)s.%(ext)s',
}

class Downloader():
    def __init__(self, name):
        self.name = name
        self.history = []

    def download(self, link):
        self.link = link
        self.history.append(self.link)
        print(f"Робот скачивает: {self.link}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Тут тоже через подчеркивание
            ydl.download([self.link])

    def show_history(self):
        for i in self.history:
            print(f"Робот {self.name} успешно скачал: {i}")

bot = Downloader("Максим")

@app.route("/download")
def download_page():
    # Вытаскиваем параметр 'link' из адреса страницы
    user_link = request.args.get('link') 
    if user_link:
        bot.download(user_link)
    
        return render_template("success.html", site=user_link)
    else:
        return f"Ошибка: вы не указали ссылку!"

@app.route("/history")
def history_page():
    # Мы не склеиваем строку сами, а отдаем список и имя шаблону
    return render_template("history.html", bot_name=bot.name, links=bot.history)

@app.route("/")
def index():
    return render_template("index.html", bot_name=bot.name)

if __name__ == "__main__":
    app.run(debug=True) # Запускаем локальный сервер
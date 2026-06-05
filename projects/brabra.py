import random # Это нам нужно только для примера

links = [
    "mysong.mp3"
]

filename = []


for link in links:
    title = f"Формат песни {link[-3:]}"
    size = random.randint(10, 100)

    new_video = {
        "title": title,
        "size": size
    }

    filename.append(new_video)

for music in filename:
    print(f"Готово к скачиванию: {music['title']} | Размер: {music['size']} MB")
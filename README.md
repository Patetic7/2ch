1. Скачать репу:
```console
git clone https://github.com/Patetic7/2ch.git
```

или

```console
git clone git@github.com:Patetic7/2ch.git
```

2. Вход:
```console
cd 2ch
```

3. Виртуальное окружение:
```console
python3 -m venv venv
source venv/bin/activate
```

4. Установка зависимостей:
```console
pip install -U pip
pip install -r requirements.txt
```

Схема корректной команды: `python3 2ch.py <путь к папке сохранения> <img | vid | both> <ссылка на первый тред> <ссылка на второй тред> ... <ссылка на последний тред>`

`img` - изображения

`vid` - видео

`both` - изображения и видео

Пример (качаем все медиафайлы с одного треда и сохраняем в заранее созданную папку `2ch` в папке `Downloads`):
```console
python3 2ch.py ~/Downloads/2ch both https://2ch.org/b/res/329415505.html
```

5. Пользуйся!

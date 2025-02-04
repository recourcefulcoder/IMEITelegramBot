# TelegramApiBot

Telegram bot (bot.py) must be activated in a different process after starting an API;

assuming you have already installed all required packages and switched to imei/api, firstly
start an API:
```bash
python manage.py runserver
```

then, in different CLI, start bot:
```bash
python bot.py
```

# TelegramApiBot

Telegram bot (bot.py) must be activated in a different process after starting an API;

assuming you have already installed all required packages and switched to imei/api, firstly
start an API:
```bash
sanic server:app
```

bot is sarted automatically; however, if you want to activate bot sepcifically, you will 
have to provide api-path argument in CLI command, just like that:

```bash
python bot.py --api-path <your_path_here>
```

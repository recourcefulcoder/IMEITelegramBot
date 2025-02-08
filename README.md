# TelegramApiBot

### Description

This program - is a Sanic-based API-service for sending requests to the [imeicheck api](https://imeicheck.net/promo-api),
with telegram bot integrated.


### Running guide 
assuming you have already installed all required packages and switched to imei/api, firstly
start an API:
```bash
sanic server:app
```

bot is started automatically; however, if you want to activate bot explicitly, you will 
have to provide api-path argument in CLI command, just like that:

```bash
python bot.py --api-path <your_path_here>
```

### Docs
Whole logic is stored in two separate files:
+ _server.py_, which describes Sanic server
+ _bot.py_, which states telegram bot (using aiogram)

> [!WARNING]
> server.py contains constant called BOTFILE_NAME, which stores the name of python file, 
> describing the bot behavior; if you will EVER change this file's name/location, make sure 
> to change this constant on your own!


Environmental variables:
+ **BOT_TOKEN** - stores [telegram bot token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
+ **IMEICHECK_TOKEN** - stores token for accessing [imeicheck.net API](https://imeicheck.net/promo-api)


#### File-stored constants:
##### server.py
+ **IMEICHECK_URL** representing outer API-service URL
+ **IMEICHEK_TOKEN** representing token for access to outer API
+ **BOTFILE_NAME** repressenting name of python file, containing telegram bot logic, 
related to current server.py file location

##### bot.py
+ **TOKEN** representing telegram bot token
+ **BOT_USERNAME**
+ **API_PATH** representing URL to API bot is addressing to
+ **ID_WHITELIST** - set of ints, representing allowed telegram user id's

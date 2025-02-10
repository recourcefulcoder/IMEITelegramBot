# TelegramApiBot

### Description

This program - is a Sanic-based API-service for sending requests to the [imeicheck api](https://imeicheck.net/promo-api),
with telegram bot integrated.


### Running guide 
assuming you have already installed all required packages and switched to imei/api, tu run an API 
in debug mode run the following command in CLI:
```bash
sanic server:app --debug
```

bot is started automatically; however, if you want to activate bot explicitly, you will 
have to provide api-path argument in CLI command. Supported arguments for running bot.py are:
+ --api-url (defaults to "http://localhost:8000") - represents URL of API-service for bot to interact with
+ --refresh-end (defaults to "refresh/") - represents API endpoint for refreshing access token
+ --login-end (defaults to "login/") - represents API login endpoint
+ --main-end (defaults to "/check-imei") - represents API endpoint which handles main functionality 
(translating IMEI check request to side API)

you can run bot explicitly with this command:
```bash
python bot.py --api-url <your_path_here> --login-url <corresponsing endpoint> --refresh-end <corr. endpoint> --main-end <corr.endpoint>
```

### Docs
Whole logic is stored in two separate files:
+ _server.py_, which describes Sanic server
+ _bot.py_, which states telegram bot (using aiogram)

> [!WARNING]
> server.py contains constant called BOTFILE_NAME, which stores the name of python file, 
> describing the bot behavior; if you will EVER change this file's name/location, make sure 
> to change this constant on your own!

> [!CAUTION]
> Since database is not included in the project yet, it uses some _temporary_ improper storages of 
> login credentials - Bot's password for accessing API is stored in an environment variable, for example,
> as you will see lower. This must be changed in production use, yet is not in a current state.

Environmental variables:
+ **BOT_TOKEN** - stores [telegram bot token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
+ **IMEICHECK_TOKEN** - stores token for accessing [imeicheck.net API](https://imeicheck.net/promo-api)
+ **API_BOT_PASSWORD** - Bot's password for accessing API
+ **SECRET_KEY** - used for JWT-based auth

#### File-stored constants:
##### server.py
+ **IMEICHECK_URL** representing outer API-service URL
+ **IMEICHEK_TOKEN** representing token for access to outer API
+ **BOTFILE_NAME** repressenting name of python file, containing telegram bot logic, 
related to current server.py file location

##### bot.py
+ **TOKEN** representing telegram bot token
+ **BOT_USERNAME**
+ **ID_WHITELIST** - set of ints, representing allowed telegram user id's
+ **API_URL** representing URL to API bot is addressing to for main functionality
+ **LOGIN_ENDPOINT** representing API's _login_ url
+ **MAIN_ENDPOINT** representing API's _main_ url
+ **REFRESH_ENDPOINT** representing API's _refresh_ url
+ **API_PASSWORD** storing token for accessing the API

##### login.py
+ **refresh_tokens** - temporary solution for storing refreshed tokens without database connected;
used in sevrer.py file in authorization purposes

### Auth mechanism
When logging in, bot sends json payload which looks like following: 
```python
{
    "password": BOT_PASSWORD
}
```
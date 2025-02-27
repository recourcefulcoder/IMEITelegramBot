# TelegramApiBot

### Description

This program - is a Sanic-based API-service for sending requests to the [imeicheck api](https://imeicheck.net/promo-api),
with telegram bot integrated.


### Running guide 

#### Install requirements
Install all the required packages by running
```bash
pip install -r requirements.txt
```

Your machine should have a redis server installed and ready-to go, defaulting to port 6379.

On linux you can install it using 
```bash
sudo apt-get install redis-server
```

#### Create database tables
you can make it by running following from "src" directory of the project: 
```bash
python database/create_database.py
```

#### Create environment file
Create .env file in the root directory of the project and fill it as .env.example; required env variables
are described below

#### Create whitelist.json

In the source directory of the project (i.e. "src"), on the same level as "config.py" file create file
"whitelist.json", which contains a json-string, describing all Telegram user ID's those are allowed to 
access the bot; it must look like following:
```json
[
  7835373821, 8338273811, 7835374311, ...
]
```

#### Run the application
to run an API in debug mode run the following command in CLI (being in the "src" directory of the project):
```bash
sanic server:create_app --debug
```

bot is started automatically on a project setup; 

Loading it on your own is **DEPRICATED** as it uses environmental variables loaded in server.py file;

However, if you want to activate bot explicitly, you can do that (assuming you took care of loading crucial
environment variables on your own) from standard CLI interface, yet _you should provide some arguments_. 
Supported arguments for running bot.py are:
+ --api-url (defaults to "http://localhost:8000") - represents URL of API-service for bot to interact with
+ --refresh-end (defaults to "refresh/") - represents API endpoint for refreshing access token
+ --login-end (defaults to "login/") - represents API login endpoint
+ --main-end (defaults to "/check-imei") - represents API endpoint which handles main functionality 
(translating IMEI check request to side API)

you can run bot explicitly with this command:
```bash
python bot.py --api-url <your_path_here> --login-url <corresponsing endpoint> --refresh-end <corr. endpoint> --main-end <corr.endpoint>
```

> [!WARNING]
> API has a JWT-based auth system; it logs in users and gives them a token. BOT is a user as well,
> so in order to grant him access you should add your bot to the PostgreSQL database specified for 
> the project and pass its credentials via corresponding environment variables (see below)


## Docs
Whole logic is stored in two separate files:
+ _server.py_, which describes Sanic server
+ _bot.py_, which states telegram bot (using aiogram)

Environmental variables:
+ **BOT_TOKEN** - stores [telegram bot token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
+ **IMEICHECK_TOKEN** - stores token for accessing [imeicheck.net API](https://imeicheck.net/promo-api)
+ **API_BOT_USERNAME** - stores username of BOT in API's database's users table; defaults 
to "TELEGRAM_BOT" if not provided
+ **API_BOT_PASSWORD** - Bot's password for accessing API
+ **SECRET_KEY** - used for JWT-based auth
+ **POSTGRES_PASSWORD** - stores database password
+ **HOSTNAME** - stores the name of the host to be used; for docker environments will be 
host.docker.internal

### Constants
Majority of used constants are stored in _config.py_, except for a few related to bot, stored in _bot.py_ 
##### config.py
+ **IMEICHECK_URL** representing outer API-service URL
+ **IMEICHEK_TOKEN** representing token for access to outer API
+ **BOTFILE_NAME** repressenting name of python file, containing telegram bot logic, 
related to current config.py file location
+ **BOT_TOKEN** representing telegram bot token
+ **ID_WHITELIST** - set of ints, representing allowed telegram user id's
+ **API_PASSWORD** storing token for logging in on the API
+ **API_BOT_USERNAME** storing bot's login username for API; defaults to "TELEGRAM_BOT" if corresponding
environment variable is not provided


+ **JWT_SECRET_KEY** - secret key value, used for scryptographical purposes
+ **POSTGRES_PASSWORD** - password for accessing postgresql database 
+ **REDIS_URL** - url for accessing Redis-storage database (used for storing access tokens)
+ **REFRESH_TOKEN_EXPIRE** - [datetime.datetime](https://docs.python.org/3/library/datetime.html#datetime-objects) 
object, representing lifetime of refresh token
+ **ACCESS_TOKEN_EXPIRE** - datetime.datetime object, representing lifetime of access JWT token

> [!WARNING]
> config.py contains constant called BOTFILE_NAME, which stores the name of python file, 
> describing the bot behavior; if you will EVER change this file's name/location, make sure 
> to change this constant on your own!

##### bot.py
+ **API_URL** representing URL to API bot is addressing to for main functionality
+ **LOGIN_ENDPOINT** representing API's _login_ url
+ **MAIN_ENDPOINT** representing API's _main_ url
+ **REFRESH_ENDPOINT** representing API's _refresh_ url

##### login.py
+ **refresh_tokens** - temporary solution for storing refreshed tokens without database connected;
used in sevrer.py file in authorization purposes

### Authentication/authorization mechanism
When logging in, bot sends json payload which looks like following: 
```python
{
    "username": BOT_USERNAME,
    "password": BOT_PASSWORD,
}
```
If credentials are valid, he resievces JSON Web Token (so-called access_token) with expiration 
date of 15mins and a refresh_token, which lasts for 14days.

Refresh tokens are stored in a redis storage

 Auth logic is implemented in _auth.py_ file and /refresh endpoint of server.py

 ##### auth.py
+ def protected() -- decorator for endpoint handlers which checks if user's token valid or not and
restricts access if os not
+ class TokenManager - implements logic of interaction with redis storage. Details - lower

**class TokenManager** attributes:
+ redis - stores Redis object of redis module
> [!WARNING]
> "redis" attribute must be initialized before usage of class by calling "init_redis" coroutine

**class TokenManager** methods:

(all defined as coroutines)
+ create_access_token(identity: str) - static method, creates new access_token via jwt module;

_**identity used is user's USERNAME**_
+ create_refresh_token(self, username: str) -> str - creates new refresh token based on user's username, 
stores it in redis storage and returns token as a return-value
+ verify_refresh_token(self, refresh_token: str) -> Optional[str] - accepts refresh token and looks for
such in redis storage; if it finds such token, it returns user's username; if it doesn't - it returns None
+ delete_refresh_token(self, username: str) -> None - accepts username whose refresh_token is stored in redis
and deletes it from redis storage.

### Docker
To run a server with redis and postgres as special containers, simply run from the project root directory
```bash
docker build -t imei-app:1.0 .
docker-compose -f docker-compose.yaml up
```

### Test
For running test, from the source directory of the project (i.e. "/src") run following:
```bash
python -m pytest
```


# Project-Siesta
![GitHub Repo stars](https://img.shields.io/github/stars/vinayak-7-0-3/Project-Siesta?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/vinayak-7-0-3/Project-Siesta?style=for-the-badge)
![Docker Pulls](https://img.shields.io/docker/pulls/weebzbots/project-siesta?style=for-the-badge)
[![Static Badge](https://img.shields.io/badge/support-pink?style=for-the-badge)](https://t.me/weebzgroup)

AIO Bot for your music needs on Telegram.

Note: This is not a music streaming / VC Bot

## FEATURES

**Currently the project is in early development stage and features are incomplete**

Feels free to check the repo and report bugs / features

## INSTALLATION

- Clone the repo (download it or git clone)

#### 1) LOCAL DEPLOYMENT

**Requirements**
- Python>=3.10 (3.12 recommended) 
- Rclone (optional)

Create virtual environment and run
```
virtualenv -p python3 VENV
. ./VENV/bin/activate
```
Edit and fill out the essentials environment variables in `sample.env` (refer [here](#variables-info))

Rename `sample.env` to `.env`

Finally run
```
pip install -r requirements.txt
python -m bot
```

#### 2) USING DOCKER (Manual Build)
**Requirements**
- Docker installed

Edit and fill out the essentials environment variables in `sample.env` (refer [here](#variables-info))

Rename `sample.env` to `.env`

Make docker image

```
sudo docker build . -t projectsiesta
```

Run the docker image

```
sudo docker run -d --name siesta projectsiesta
```

#### 3) USING DOCKER (Prebuilt Image)

You can find prebuilt images using github actions at Dockerhub repo - `weebzbots/project-siesta`

Tags: 
- `latest` - latest built from main brach
- `beta` - latest beta updates (for testing)

You can use commit-hash as tag for specific versions

Pull the docker image using

```
sudo docker pull weebzcloud/project-siest
```
Create a `.env` file with essential variables (refer [here](#variables-info))

Run the docker image

```
sudo docker run -d --env-file .env --name siesta projectsiesta
```

## VARIABLES INFO

#### ESSENTIAL VARIABLES
- `TG_BOT_TOKEN` - Telegeam bot token (get it from [BotFather](https://t.me/BotFather))
- `APP_ID` - Your Telegram APP ID (get it from my.telegram.org) `(int)`
- `API_HASH` - Your Telegram APP HASH (get it from my.telegram.org) `(str)`
- `DATABASE_URL` - Postgres database URL (self hosted or any service) `(str)`
- `BOT_USERNAME` - Your Telegram Bot username (with or without `@`) `(str)`
- `ADMINS` - List of Admin users for the Bot (seperated by comma) `(str)`

#### OPTIONAL VARIABLES
- `DOWNLOAD_BASE_DIR` - Downloads folder for the bot (folder is inside the working directory of bot) `(str)`
- `LOCAL_STORAGE` - Folder (full path needed) where you want to store the downloaded file the server itself rather than uploading `(str)`
- `RCLONE_CONFIG` - Rclone config as text or URL to file (can ignore this if you add file manually to root of repo) `(str)`
- `RCLONE_DEST` - Rclone destination as `remote-name:folder-in-remote` `(str)`
- `INDEX_LINK` - If index link needed for Rclone uploads (testes with alist) (no trailing slashes `/` ) `(str)`
- `MAX_WORKERS` - Multithreading limit (kind of more speed) `(int)`
- `TRACK_NAME_FORMAT` - Naming format for tracks (check [metadata](https://github.com/vinayak-7-0-3/Project-Siesta/blob/2bbea8572d660a92bb182a360e91791583f4523b/bot/helpers/metadata.py#L16) section for tags supported) `(str)`
- `PLAYLIST_NAME_FORMAT` - Similar to `TRACK_NAME_FORMAT` but for Playlists (Note: all tags might not be available) `(str)`
- `QOBUZ_EMAIL` - Email ID for logging into Qobuz `(str)`
- `QOBUZ_PASSWORD` - Password for logging into Qobuz `(str)`
- `QOBUZ_USER` - User ID for Qobuz (either use Email or this) `(int)`
- `QOBUZ_TOKEN` - User token for Qobuz (either use password or this) `(str)`
- `ENABLE_TIDAL` - To enable the Tidal module - True/False `(bool)`
- `TIDAL_MOBILE` - To enable Tidal Mobile sessions - True/False `(bool)`
- `TIDAL_MOBILE_TOKEN` - HiRes Mobile token for Tidal `(str)`
- `TIDAL_ATMOS_MOBILE_TOKEN` - Atmos Mobile token for Tidal `(str)`
- `TIDAL_TV_TOKEN` - TV/Auto Token for Tidal `(str)`
- `TIDAL_TV_SECRET` - TV/Auto Token for Tidal `(str)`

## CREDITS
- OrpheusDL - https://github.com/yarrm80s/orpheusdl
- Streamrip - https://github.com/nathom/streamrip
- yaronzz - Tidal-Media-Downloader - https://github.com/yaronzz/Tidal-Media-Downloader
- vitiko98 - qobuz-dl - https://github.com/vitiko98/qobuz-dl

## Support Me ❤️
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/I2I7FWQZ4)

TON - `UQBBPkWSnbMWXrM6P-pb96wYxQzLjZ2hhuYfsO-N2pVmznCG`
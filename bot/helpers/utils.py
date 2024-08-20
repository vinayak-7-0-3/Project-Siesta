import os
import aiohttp
import asyncio
import shutil

from config import Config
from bot.settings import bot_set

from .message import send_message
from ..logger import LOGGER


async def download_file(url, path):
    """path : including filename with extention"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                return None
            else:
                return "HTTP Status: {response.status}"

async def format_string(text:str, data:dict, user=None):
    """
    text: text to be formatted
    data: source info
    user: user details
    """
    text = text.replace(R'{title}', data['title'])
    text = text.replace(R'{album}', data['album'])
    text = text.replace(R'{artist}', data['artist'])
    text = text.replace(R'{albumartist}', data['albumartist'])
    text = text.replace(R'{tracknumber}', str(data['tracknumber']))
    text = text.replace(R'{date}', str(data['date']))
    text = text.replace(R'{upc}', str(data['upc']))
    text = text.replace(R'{isrc}', str(data['isrc']))
    text = text.replace(R'{totaltracks}', str(data['totaltracks']))
    text = text.replace(R'{volume}', str(data['volume']))
    text = text.replace(R'{totalvolume}', str(data['totalvolume']))
    text = text.replace(R'{extension}', data['extension'])
    text = text.replace(R'{duration}', str(data['duration']))
    text = text.replace(R'{copyright}', data['copyright'])
    text = text.replace(R'{genre}', data['genre'])
    text = text.replace(R'{provider}', data['provider'].title())
    text = text.replace(R'{quality}', data['quality'])
    text = text.replace(R'{explicit}', str(data['explicit']))
    if user:
        text = text.replace(R'{user}', user['name'])
        text = text.replace(R'{username}', user['user_name'])
    return text


async def run_concurrent_tasks(tasks, update=None):
    semaphore = asyncio.Semaphore(Config.MAX_WORKERS)

    i = [0]
    async def sem_task(task):
        async with semaphore:
            result = await task
            if update and result:
                i[0]+=1
                edit_msg = update['func']
                try:
                    await edit_msg(update['param'], update['text'].format(i[0], len(tasks)))
                except:
                    pass

    await asyncio.gather(*(sem_task(task) for task in tasks))

async def handle_upload(filepath, batch=False, meta=None, user=None):
    path = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/"

    if bot_set.upload_mode == 'Local':
        for item in os.listdir(path):
            source_path = os.path.join(path, item)
            if os.path.isdir(source_path):
                to_move = os.path.join(Config.LOCAL_STORAGE, item)
                shutil.move(source_path, to_move)
    
    if batch:
        if bot_set.upload_mode == 'Telegram':
            for track in meta:
                thumb = track['filepath'].replace(track['extension'], 'jpg')
                await download_file(track['thumbnail'], thumb)
                await send_message(user, track['filepath'], 'audio', thumb=thumb, meta=track)
        else:
            await run_rclone(path)
    else:
        if bot_set.upload_mode == 'Telegram':
            thumb = meta['filepath'].replace(meta['extension'], "jpg")
            await download_file(meta['thumbnail'], thumb)
            await send_message(user, filepath, 'audio', thumb=thumb, meta=meta)
        else:
            await run_rclone(path)


async def run_rclone(to_upload):
    cmd = f'rclone copy --config ./rclone.conf "{to_upload}" "{Config.RCLONE_DEST}"'
    task = await asyncio.create_subprocess_shell(cmd)
    await task.wait()

async def cleanup(user):
    try:
        shutil.rmtree(f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/")
    except Exception as e:
        LOGGER.info(e)
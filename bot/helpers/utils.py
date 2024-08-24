import os
import math
import aiohttp
import asyncio
import shutil

from pathlib import Path
from urllib.parse import quote

from config import Config

from ..logger import LOGGER
from ..settings import bot_set
from .translations import lang
from .buttons.links import links_button
from .message import send_message, edit_message


# download folder structure : BASE_DOWNLOAD_DIR + message_r_id

async def download_file(url, path):
    """
    Args:
        url : to download
        path : including filename with extention
    Returns:
        Error if any else None
    """
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
    Args:
        text: text to be formatted
        data: source info
        user: user details
    Returns:
        str
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
    """
    Args:
        tasks: (list) async functions to be run
        update: whether to show progress updates    
    """
    semaphore = asyncio.Semaphore(Config.MAX_WORKERS)

    i = [0]
    async def sem_task(task):
        async with semaphore:
            result = await task
            if update and result:
                i[0]+=1 # currently done
                await progress_message(i[0], len(tasks), update)

    await asyncio.gather(*(sem_task(task) for task in tasks))



async def handle_upload(batch=False, metadata=None, user=None):
    """
    Args:
        batch: (bool)
        metadata: full metadata
    """
    # metadata contains filepath(if single file) and folderpath(if batch)
    # rclone will not upload the given folder (but files/folder inside the given folder)
    path = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/"
    link_button = None

    # just move the folders to local path provided
    if bot_set.upload_mode == 'Local':
        to_move = path + metadata['provider']
        shutil.move(to_move, Config.LOCAL_STORAGE)
        return
    
    if batch:
        if bot_set.upload_mode == 'Telegram':
            for track in metadata['tracks']:
                thumb = track['filepath'].replace(track['extension'], 'jpg')
                await download_file(track['thumbnail'], thumb)
                await send_message(user, track['filepath'], 'audio', thumb=thumb, meta=track)
        else:
            await run_rclone_upload(path)
            link_button = await create_link_markup(metadata['folderpath'], path)
    else:
        if bot_set.upload_mode == 'Telegram':
            thumb = metadata['filepath'].replace(metadata['extension'], "jpg")
            await download_file(metadata['thumbnail'], thumb)
            await send_message(user, metadata['filepath'], 'audio', thumb=thumb, meta=metadata)
        else:
            await run_rclone_upload(path)
            link_button = await create_link_markup(metadata['filepath'], path)

    # send/edit message with link
    # only works for rclone uploads
    if link_button:
        if bot_set.alb_art and metadata['message']:
                await post_album_art(user, metadata, True, link_button)
        else:
            await send_message(
                user, 
                lang.SIMPLE_TITLE.format(
                    metadata['title'],
                    metadata['type'].title(),
                    metadata['provider']
                ),
                markup=link_button
            )

async def run_rclone_upload(to_upload):
    cmd = f'rclone copy --config ./rclone.conf "{to_upload}" "{Config.RCLONE_DEST}"'
    task = await asyncio.create_subprocess_shell(cmd)
    await task.wait()


async def create_link_markup(path, basepath):
    """
    Args:
        path: full real path
        basepath: to remove bot folder from real path (DOWNLOADS/r_id/)
    Returns:
        InlineKeyboardMarkup
    """
    path = str(Path(path).relative_to(basepath))

    rclone_link = None
    index_link = None

    if bot_set.link_options == 'RCLONE' or bot_set.link_options=='Both':
        cmd = f'rclone link --config ./rclone.conf "{Config.RCLONE_DEST}/{path}"'
        task = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await task.communicate()

        if task.returncode == 0:
            rclone_link = stdout.decode().strip()
        else:
            error_message = stderr.decode().strip()
            LOGGER.debug(f"Failed to get link: {error_message}")
    if bot_set.link_options == 'Index' or bot_set.link_options=='Both':
        if Config.INDEX_LINK:
            index_link =  Config.INDEX_LINK + '/' + quote(path)

    if rclone_link or index_link:
        return links_button(rclone_link, index_link)
    else:
        return None



async def post_album_art(user:dict, meta:dict, edit=False, markup=None):
    """
    Args:
        edit: whether to edit existing post
        markup: buttons if needed
    Returns:
        Message
    """
    caption = await format_string(lang.ALBUM_TEMPLATE, meta, user)
    if edit:
        return await edit_message(meta['message'], caption, markup)
    if bot_set.alb_art:
        msg = await send_message(user, meta['cover'], 'pic', caption)
        meta['message'] = msg



async def progress_message(done, total, details):
    """
    Args:
        done: how much task done
        total: total number of tasks
        details: title, func
    """
    progress_bar = "{0}{1}".format(
        ''.join(["▰" for i in range(math.floor((done/total) * 10))]),
        ''.join(["▱" for i in range(10 - math.floor((done/total) * 10))])
    )

    try:
        await details['func'](
            details['msg'],
            details['text'].format(
                progress_bar, 
                done, 
                total, 
                details['title'],
                details['type'].title()
            )
        )
    except:pass



async def cleanup(user):
    try:
        shutil.rmtree(f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/")
    except Exception as e:
        LOGGER.info(e)
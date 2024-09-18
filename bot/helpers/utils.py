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



async def rclone_upload(user, realpath):
    """
    Args:
        user: user details
        realpath: full path to (not used for uploading)
    Returns:
        rclone_link, index_link
    """
    path = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/"
    cmd = f'rclone copy --config ./rclone.conf "{path}" "{Config.RCLONE_DEST}"'
    task = await asyncio.create_subprocess_shell(cmd)
    await task.wait()
    r_link, i_link = await create_link(realpath, Config.DOWNLOAD_BASE_DIR + f"/{user['r_id']}/")
    return r_link, i_link


async def local_upload(metadata, user):
    path = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/"
    to_move = path + metadata['provider']
    shutil.move(to_move, Config.LOCAL_STORAGE)


async def init_telegram_upload(metadata, user):
    """
    Set up telegram to upload only a single track at once
    Args:
        metadata: full metadata
        user: user details
    """
    if metadata['type'] == 'album' or metadata['type'] == 'playlist':
        for track in metadata['tracks']:
            await telegram_upload(track, user)
    elif metadata['type'] == 'artist':
        for album in metadata['albums']:
            for track in album['tracks']:
                await telegram_upload(track, user)

# simple single track upload
async def telegram_upload(track, user):
    thumb = track['filepath'].replace(track['extension'], 'jpg')
    await download_file(track['thumbnail'], thumb)
    await send_message(user, track['filepath'], 'audio', thumb=thumb, meta=track)


async def create_link(path, basepath):
    """
    Args:
        path: full real path
        basepath: to remove bot folder from real path (DOWNLOADS/r_id/)
    Returns:
        rclone_link: link from rclone
        index_link: index link if enabled
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

    return rclone_link, index_link


async def zip_folder(folderpath):
    """
    Args:
        folderpath: to zip
    Returns:
        path to zip file
    """
    zip_path = f"{folderpath}.zip"
    shutil.make_archive(folderpath, 'zip', folderpath)
    return zip_path


async def post_art_poster(user:dict, meta:dict, edit=False, markup=None):
    """
    Args:
        edit: whether to edit existing post
        markup: buttons if needed
    Returns:
        Message
    """
    if meta['type'] == 'album':
        caption = await format_string(lang.ALBUM_TEMPLATE, meta, user)
        photo = meta['cover']
    else:
        caption = await format_string(lang.PLAYLIST_TEMPLATE, meta, user)
        photo = "./project-siesta.png"
    
    if edit:
        return await edit_message(meta['poster_msg'], caption, markup)
    if bot_set.art_poster:
        msg = await send_message(user, photo, 'pic', caption)
        return msg


async def post_simple_message(user, meta, r_link=None, i_link=None):
    """
    Sends a simple message of item with button
    Args:
        user: user details
        meta: metadata
        markup: buttons if needed
    Returns:
        Message
    """
    caption = await format_string(
        lang.SIMPLE_TITLE.format(
            meta['title'],
            meta['type'].title(),
            meta['provider']
        ), 
        meta, 
        user
    )
    markup = links_button(r_link, i_link)
    if meta['type'] == 'album':
        if meta['poster_msg']:
            await post_art_poster(user, meta, True, markup)
    else:
        await send_message(user, caption, markup=markup)


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
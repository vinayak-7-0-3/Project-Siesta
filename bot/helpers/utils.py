import os
import math
import aiohttp
import asyncio
import shutil
import zipfile

from pathlib import Path
from urllib.parse import quote
from aiohttp import ClientTimeout
from pyrogram.errors import MessageNotModified
from concurrent.futures import ThreadPoolExecutor
from pyrogram.errors import FloodWait

from config import Config
import bot.helpers.translations as lang

from ..logger import LOGGER
from ..settings import bot_set
from .buttons.links import links_button
from .message import send_message, edit_message


MAX_SIZE = 1.9 * 1024 * 1024 * 1024  # 2GB
# download folder structure : BASE_DOWNLOAD_DIR + message_r_id

async def download_file(url, path, retries=3, timeout=30):
    """
    Args:
        url (str): URL to download.
        path (str): Path including filename with extension.
        retries (int): Number of retries in case of failure.
        timeout (int): Timeout duration for the request in seconds.
    Returns:
        str or None: Error message if any, else None.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    for attempt in range(1, retries + 1):
        try:
            async with aiohttp.ClientSession(timeout=ClientTimeout(total=timeout)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(path, 'wb') as f:
                            while True:
                                chunk = await response.content.read(1024 * 4)
                                if not chunk:
                                    break
                                f.write(chunk)
                        return None
                    else:
                        return f"HTTP Status: {response.status}"
        except aiohttp.ClientError as e:
            if attempt == retries:
                return f"Connection failed after {retries} attempts: {str(e)}"
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except asyncio.TimeoutError:
            if attempt == retries:
                return "Download failed due to timeout."
            await asyncio.sleep(2 ** attempt)



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



async def run_concurrent_tasks(tasks, progress_details=None):
    """
    Args:
        tasks: (list) async functions to be run
        progress_details: details for progress message (dict)    
    """
    semaphore = asyncio.Semaphore(Config.MAX_WORKERS)

    i = [0]
    l = len(tasks)
    async def sem_task(task):
        async with semaphore:
            result = await task
            if progress_details and result:
                i[0]+=1 # currently done
                await progress_message(i[0], l, progress_details)

    await asyncio.gather(*(sem_task(task) for task in tasks))


async def create_link(path, basepath):
    """
    Creates rclone and index link
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


async def zip_handler(folderpath):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        if bot_set.upload_mode == 'Telegram':
            zips = await loop.run_in_executor(pool, split_zip_folder, folderpath)
        else:
            zips = await loop.run_in_executor(pool, zip_folder, folderpath)
        return zips


def split_zip_folder(folderpath) -> list:
    """
    Args:
        folderpath: path to folder to zip
    Returns:
        list of zip file paths
    """
    zip_paths = []
    part_num = 1
    current_size = 0
    current_files = []

    def add_to_zip(zip_name, files_to_add):
        if part_num == 1:
            zip_path = f"{zip_name}.zip"
        else:
            zip_path = f"{zip_name}.part{part_num}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path, arcname in files_to_add:
                zipf.write(file_path, arcname)
                os.remove(file_path)  # Delete the file after zipping
        return zip_path

    for root, dirs, files in os.walk(folderpath):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            arcname = os.path.relpath(file_path, folderpath)

            # If adding this file would exceed the max size, create a zip for the current files
            if current_size + file_size > MAX_SIZE:
                zip_paths.append(add_to_zip(folderpath, current_files))
                part_num += 1
                current_files = []  # Reset for the next zip part
                current_size = 0

            # Add the file to the current group
            current_files.append((file_path, arcname))
            current_size += file_size

    # Create the final zip with any remaining files
    if current_files:
        zip_paths.append(add_to_zip(folderpath, current_files))

    return zip_paths


def zip_folder(folderpath) -> str:
    """
    Args:
        folderpath (str): The path of the folder to zip.
    Returns:
        str: The path to the created zip file.
    """
    zip_path = f"{folderpath}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folderpath):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folderpath))
                # Remove file after adding to the zip
                os.remove(file_path)
    
    return zip_path


async def move_sorted_playlist(metadata, user) -> str:
    """
    Moves the sorted playlist files into a new playlist folder.
    Used since sorted tracks doest belong to a specific palylist folder
    Returns:
        str: path to the newly created playlist folder
    """

    source_folder = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{metadata['provider']}"
    destination_folder = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{metadata['provider']}/{metadata['title']}"

    os.makedirs(destination_folder, exist_ok=True)

    # get list of folders inside the source
    folders = [
        os.path.join(source_folder, name) for name in os.listdir(source_folder) if os.path.isdir(os.path.join(source_folder, name))
    ]

    for folder in folders:
        shutil.move(folder, destination_folder)

    return destination_folder


async def post_art_poster(user:dict, meta:dict):
    """
    Args:
        markup: buttons if needed
    Returns:
        Message
    """
    if meta['type'] == 'album':
        caption = await format_string(lang.s.ALBUM_TEMPLATE, meta, user)
        photo = meta['cover']
    else:
        caption = await format_string(lang.s.PLAYLIST_TEMPLATE, meta, user)
        photo = "./project-siesta.png"
    
    if bot_set.art_poster:
        msg = await send_message(user, photo, 'pic', caption)
        return msg


async def create_simple_text(meta, user):
    caption = await format_string(
        lang.s.SIMPLE_TITLE.format(
            meta['title'],
            meta['type'].title(),
            meta['provider']
        ), 
        meta, 
        user
    )
    return caption


async def edit_art_poster(metadata, user, r_link, i_link, caption):
    """
    Edits Album/Playlist Art Poster with given information
    Args:
        metadata: metadata dict of item
        caption: text to edit
    """
    markup = links_button(r_link, i_link)
    await edit_message(
        metadata['poster_msg'],
        caption,
        markup
    )


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
    caption = await create_simple_text(meta, user)
    markup = links_button(r_link, i_link)
    await send_message(user, caption, markup=markup)


async def progress_message(done, total, details):
    """
    Args:
        done: how much task done
        total: total number of tasks
        details: Message, text (dict)
    """
    progress_bar = "{0}{1}".format(
        ''.join(["▰" for i in range(math.floor((done/total) * 10))]),
        ''.join(["▱" for i in range(10 - math.floor((done/total) * 10))])
    )

    try:
        await edit_message(
            details['msg'],
            details['text'].format(
                progress_bar, 
                done, 
                total, 
                details['title'],
                details['type'].title()
            ),
            None,
            False
        )
    except FloodWait as e:
        pass # dont update the message if flooded


async def cleanup(user=None, metadata=None, ):
    """
    Clean up after task completed / Clean up after upload
    if metadata
        Artist/Album/Playlist files are deleted
    if user
        user root folder is removed
    
    """
    if metadata:
        try:
            if metadata['type'] == 'album':
                is_zip = True if bot_set.album_zip else False
            elif metadata['type'] == 'artist':
                is_zip = True if bot_set.artist_zip else False
            else:
                is_zip = True if bot_set.playlist_zip else False
            if is_zip:
                if type(metadata['folderpath']) == list:
                    for i in metadata['folderpath']:
                        os.remove(i)
                else:
                    os.remove(metadata['folderpath'])
            else:
                shutil.rmtree(metadata['folderpath'])
        except FileNotFoundError:
            pass
    if user:
        try:
            shutil.rmtree(f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/")
        except Exception as e:
            LOGGER.info(e)
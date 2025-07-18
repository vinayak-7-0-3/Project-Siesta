from pathvalidate import sanitize_filepath
from config import Config

from .metadata import *
from .dzapi import deezerapi

from ..utils import *
from ..uploder import *
from ..metadata import set_metadata, get_audio_extension

from ...settings import bot_set
import bot.helpers.translations as lang




async def start_deezer(url:str, user: dict):
    media_type, item_id = await deezerapi.custom_url_parse(url)

    if media_type == 'artist':
        await start_artist(item_id, user)
    elif media_type == 'track':
        await start_track(item_id, user, None)
    elif media_type == 'album':
        await start_album(item_id, user)
    elif media_type == 'playlist':
        await start_playlist(item_id, user)


async def start_track(item_id: int, user: dict, track_meta: dict | None, upload=True, \
    filepath=None):

    if not track_meta:
        if int(item_id) < 0: # For user uploaded
            raw_data = await deezerapi.get_track_data(item_id)
        else:
            raw_data = await deezerapi.get_track(item_id)

        raw_data['DATA'] = raw_data['FALLBACK'] if 'FALLBACK' in raw_data.keys() else raw_data['DATA']
        try:
            track_meta = await process_track_metadata(item_id, user['r_id'])
        except Exception as e:
            return await send_message(user, e)
            
        filepath = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{track_meta['provider']}/{track_meta['albumartist']}/{track_meta['album']}"

    url = await deezerapi.get_track_url(
        item_id, 
        track_meta['token'], 
        track_meta['token_expiry'], 
        track_meta['quality'])

    track_meta['folderpath'] = filepath
    filename = await format_string(Config.TRACK_NAME_FORMAT, track_meta, user)

    track_meta['extension'] = 'flac' if track_meta['quality'] == 'FLAC' else 'mp3'

    filepath += f"/{filename}.{track_meta['extension']}"
    track_meta['filepath'] = filepath = sanitize_filepath(filepath)

    await deezerapi.dl_track(item_id, url, track_meta['filepath'])

    await set_metadata(track_meta)

    if upload:
        await track_upload(track_meta, user, False)

    return True


async def start_album(album_id:int, user:dict, upload=True):
    try:
        raw_data = await deezerapi.get_album(album_id)
    except Exception as e:
        return await send_message(user, e)

    album_meta = await process_album_metadata(album_id, raw_data['DATA'], raw_data['SONGS'], user['r_id'])
    
    album_folder = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{album_meta['provider']}/{album_meta['artist']}/{album_meta['title']}"
    
    album_folder = sanitize_filepath(album_folder)
    album_meta['folderpath'] = album_folder

    if upload:
        album_meta['poster_msg'] = await post_art_poster(user, album_meta)

    # concurrent
    tasks = []
    for track in album_meta['tracks']:
        tasks.append(start_track(track['itemid'], user, track, False, album_folder))

    update_details = {
        'text': lang.s.DOWNLOAD_PROGRESS,
        'msg': user['bot_msg'],
        'title': album_meta['title'],
        'type': album_meta['type']
    }
    await run_concurrent_tasks(tasks, update_details)

    if bot_set.album_zip:
        await edit_message(user['bot_msg'], lang.s.ZIPPING)
        album_meta['folderpath'] = await zip_handler(album_meta['folderpath'])

    # Upload
    if upload:
        await edit_message(user['bot_msg'], lang.s.UPLOADING)
        await album_upload(album_meta, user)



async def start_artist(artist_id, user):
    album_ids = await deezerapi.get_artist_album_ids(artist_id, 0, -1, False)

    upload_album = True
    if bot_set.artist_batch:
        # for telegram, batch upload is not needed
        upload_album = True if bot_set.upload_mode == 'Telegram' else False
    if bot_set.artist_zip:
        upload_album = False # final decision

    for album in album_ids:
        await start_album(album, user, upload_album)


async def start_playlist(playlist_id, user):
    raw_data = await deezerapi.get_playlist(playlist_id, -1, 0)

    play_meta = await process_playlist_meta(raw_data, user['r_id'])

    playlist_folder = None

    # temp variable (telegram upload doesnt need sorting)
    playlist_sort = False if bot_set.upload_mode == 'Telegram' else bot_set.playlist_sort
    
    if not playlist_sort:
        playlist_folder = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{play_meta['provider']}/{play_meta['title']}"
        playlist_folder = sanitize_filepath(playlist_folder)
    play_meta['folderpath'] = playlist_folder


    update_details = {
        'text': lang.s.DOWNLOAD_PROGRESS,
        'msg': user['bot_msg'],
        'title': play_meta['title'],
        'type': play_meta['type']
    }

    play_meta['poster_msg'] = await post_art_poster(user, play_meta)

    upload = True
    if bot_set.playlist_conc:
        upload = False
        tasks = []
        for track in play_meta['tracks']:
            tasks.append(start_track(track['itemid'], user, track, upload, playlist_folder))
        await run_concurrent_tasks(tasks, update_details)
    else:
        i = 0
        if bot_set.playlist_zip: upload = False
        for track in play_meta['tracks']:
            await progress_message(i, len(play_meta['tracks']), update_details)
            await start_track(track['itemid'], user, track, upload, playlist_folder, bot_set.disable_sort_link, True)
            i+=1


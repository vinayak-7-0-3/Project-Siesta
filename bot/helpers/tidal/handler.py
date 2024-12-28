import json
import base64

from pathvalidate import sanitize_filepath

from .tidal_api import tidalapi
from .utils import *
from .metadata import get_track_metadata, get_album_metadata

from ..utils import *
from ..metadata import set_metadata, get_audio_extension
from ..uploder import *
from ..message import send_message

from bot.logger import LOGGER
from config import Config


async def start_tidal(url:str, user:dict):
    item_id, type_ = await parse_url(url)

    if type_ == 'track':
        await start_track(item_id, user, None)
    elif type_ == 'artist':
        pass
    elif type_ == 'album':
        await start_album(item_id, user)
    elif type_ == 'playlist':
        pass
    else:
        await send_message(user, "Invalid Tidal URL")
        

async def start_track(track_id:int, user:dict, track_meta:dict | None, \
    upload=True, basefolder=None, session=None, quality=None, disable_link=False, disable_msg=False):
    if not track_meta:
        track_data = await tidalapi.get_track(track_id)
        track_meta = await get_track_metadata(track_id, track_data)
        filepath = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{track_meta['provider']}/{track_meta['albumartist']}/{track_meta['album']}"
        # mostly session and quality will not be present
        session, quality = await get_stream_session(track_data)
    else:
        filepath = basefolder

    try:
        stream_data = await tidalapi.get_stream_url(track_id, quality, session)
    except Exception as e:
        error = e
        # definitely region locked
        if 'Asset is not ready for playback' in str(e):
            error = f'Track [{track_id}] is not available in your region'
        LOGGER.error(error)
        stream_data = None
    

    if stream_data is not None:

        track_meta['quality'] = await get_quality(stream_data)

        if stream_data['manifestMimeType'] == 'application/dash+xml':
            manifest = base64.b64decode(stream_data['manifest'])
            urls, track_codec = parse_mpd(manifest)
        else:
            manifest = json.loads(base64.b64decode(stream_data['manifest']))
            track_codec = 'AAC' if 'mp4a' in manifest['codecs'] else manifest['codecs'].upper()
            urls = manifest['urls'][0]

        
        track_meta['folderpath'] = filepath
        filename = await format_string(Config.TRACK_NAME_FORMAT, track_meta, user)
        # not adding file extention now
        filepath += f"/{filename}"
        filepath = sanitize_filepath(filepath)
        track_meta['filepath'] = filepath


        if type(urls) == list:
            i = 0   # flawless
            temp_files = []
            for url in urls[0]:
                temp_path = f"{filepath}.{i}"
                err = await download_file(url, temp_path)
                if err:
                    return await send_message(user, err)
                i+=1
                temp_files.append(temp_path)
            await merge_tracks(temp_files, filepath)
        else:
            err = await download_file(urls, filepath)
            if err:
                return await send_message(user, err)

        track_meta['extension'] = await get_audio_extension(filepath)
        track_meta['filepath'] = track_meta['filepath'] + f".{track_meta['extension']}"
        # filepath var is not updated so it contains old path before extention update
        os.rename(filepath, track_meta['filepath'])

        await set_metadata(track_meta)

        if upload:
            await track_upload(track_meta, user, False)

        

async def start_album(album_id:int, user:dict, upload=True):
    album_data = await tidalapi.get_album(album_id)
    tracks_data = await tidalapi.get_album_tracks(album_id)
    
    album_meta = await get_album_metadata(album_id, album_data, tracks_data)

    album_folder = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{album_meta['provider']}/{album_meta['artist']}/{album_meta['title']}"
    album_folder = sanitize_filepath(album_folder)
    album_meta['folderpath'] = album_folder

    # get a track to get quality
    track_id = tracks_data['items'][0]['id']
    track_data = await tidalapi.get_track(track_id)
    session, quality = await get_stream_session(track_data)
    stream_data = await tidalapi.get_stream_url(track_id, quality, session)

    album_meta['quality'] = await get_quality(stream_data)

    album_meta['poster_msg'] = await post_art_poster(user, album_meta)

    # concurrent
    tasks = []
    for track in album_meta['tracks']:
        tasks.append(start_track(track['itemid'], user, track, False, album_folder, session, quality))

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
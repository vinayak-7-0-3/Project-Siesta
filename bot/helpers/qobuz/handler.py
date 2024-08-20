from .utils import *
from config import Config

from pathvalidate import sanitize_filepath

from ..utils import download_file, run_concurrent_tasks, handle_upload
from ..metadata import set_metadata


async def start_qobuz(url:str, user:dict):
    items, item_id, type_dict, content = await check_type(url)
    if items:
        # FOR ARTIST/LABEL
        if type_dict['iterable_key'] == 'albums':
                for item in items:
                    await start_album(item['id'], user)
        else:
        # FOR PLAYLIST 
            for item in items:
                pass
                #await self.startTrack(item['id'], user)
    else:
        # FOR ALBUM
        if type_dict["album"]:
            await start_album(item_id, user)
        else:
        # FOR TRACK
            await start_track(item_id, user, None)


async def start_album(item_id:int, user:dict, upload=True, basefolder=None):
    album_meta, err = await get_album_metadata(item_id)
    if err:
        return await send_message(user, err)
    
    # Get user quality by doing a track request
    track_meta = await qobuz_api.get_track_url(album_meta['tracks'][0]['itemid'])

    _, album_meta['quality'] = await get_quality(track_meta)
    
    alb_post = await post_album_art(user, album_meta)

    if basefolder:
        pass
    else:
        album_folder = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{album_meta['provider']}/{album_meta['artist']}/{album_meta['title']}/"

    # concurrent
    tasks = []
    for track in album_meta['tracks']:
        tasks.append(start_track(track['itemid'], user, track, False, album_folder))
        
    
    update_details = {
        'text': lang.DOWNLOAD_PROGRESS,
        'func': edit_message,
        'param': user['bot_msg']
    }
    await run_concurrent_tasks(tasks, update_details)

    if upload:
        await edit_message(user['bot_msg'], lang.UPLOADING)
        await handle_upload(album_folder, True, album_meta['tracks'], user)

async def start_track(item_id:int, user:dict, track_meta:dict | None, upload=True, basefolder=None):
    if not track_meta:
        track_meta, err = await get_track_metadata(item_id)
        if err:
            return await send_message(user, err)
        filepath = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{track_meta['provider']}/{track_meta['albumartist']}/{track_meta['album']}/"
    else:
        filepath = basefolder
        
    raw_data = await qobuz_api.get_track_url(item_id)
    try:
        url = raw_data['url']
    except KeyError:
        return await send_message(user, lang.ERR_QOBUZ_NOT_AVAILABLE)
        
    track_meta['extension'], track_meta['quality'] = await get_quality(raw_data)

    filename = await format_string(Config.TRACK_NAME_FORMAT, track_meta, user)
    filepath += f"{filename}.{track_meta['extension']}"
    filepath = sanitize_filepath(filepath)
    track_meta['filepath'] = filepath

    err = await download_file(url, filepath)
    if err:
        return await send_message(user, err)
    
    await set_metadata(filepath, track_meta)

    if upload:
        await edit_message(user['bot_msg'], lang.UPLOADING)
        await handle_upload(filepath, False, track_meta, user)

    # Acknowledge task finished
    return True
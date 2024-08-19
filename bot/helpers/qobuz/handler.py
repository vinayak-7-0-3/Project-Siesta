from .utils import *
from config import Config

from pathvalidate import sanitize_filepath

from ..utils import download_file, run_concurrent_tasks


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


async def start_album(item_id:int, user:dict):
    album_meta, err = await get_album_metadata(item_id)
    if err:
        return await send_message(user, err)
    
    # Get user quality by doing a track request
    track_meta = await qobuz_api.get_track_url(album_meta['tracks'][0]['itemid'])

    _, album_meta['quality'] = await get_quality(track_meta)
    
    alb_post = await post_album_art(user, album_meta)

    album_folder = f"{Config.DOWNLOAD_BASE_DIR}/qobuz/{user['r_id']}/{album_meta['title']}/"
    # concurrent
    tasks = []
    for track in album_meta['tracks']:
        tasks.append(start_track(track['itemid'], user, track, False, album_folder))
    await run_concurrent_tasks(tasks, 5)

async def start_track(item_id:int, user:dict, track_meta:dict | None, upload=True, basefolder=None):
    if not track_meta:
        track_meta, err = await get_track_metadata(item_id)
        if err:
            return await send_message(user, err)
        filepath = f"{Config.DOWNLOAD_BASE_DIR}/qobuz/{user['r_id']}/{track_meta['album']}/"
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

    err = await download_file(url, sanitize_filepath(filepath))
    if err:
        return await send_message(user, err)
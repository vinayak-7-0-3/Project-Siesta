import shutil
from .utils import *
from config import Config

from pathvalidate import sanitize_filepath

from ..utils import *
from ..metadata import set_metadata

from ..uploder import track_upload, album_upload, artist_upload, playlist_upload


async def start_qobuz(url:str, user:dict):
    items, item_id, type_dict, content = await check_type(url)
    if items:
        # FOR ARTIST
        if type_dict['iterable_key'] == 'albums':
                await start_artist(items, user, content)
        else:
        # FOR PLAYLIST 
            await start_playlist(items, content, user)
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
    
    # for convenience, do not post album poster if artist
    if upload:
        album_meta['poster_msg'] = await post_art_poster(user, album_meta)

    if basefolder:
        album_folder = basefolder + f"/{album_meta['title']}"
    else:
        album_folder = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{album_meta['provider']}/{album_meta['artist']}/{album_meta['title']}"
    album_folder = sanitize_filepath(album_folder)
    album_meta['folderpath'] = album_folder
    
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


async def start_track(item_id:int, user:dict, track_meta:dict | None, upload=True, basefolder=None, disable_link=False, disable_msg=False):
    """
    Args:
        item_id: qobuz track id
        user: user details
        track_meta: prefetched meta
        upload: enable upload or not
        basefolder: base folder path to download track
        disable_link: disable sending rclone link as message
        disable_msg: disable uploading message
    Returns:
        Acknowledgement (bool) when finished
    """
    
    if not track_meta:
        track_meta, err = await get_track_metadata(item_id)
        if err:
            return await send_message(user, err)
        filepath = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{track_meta['provider']}/{track_meta['albumartist']}/{track_meta['album']}"
    else:
        # set base file path if doesnt exist in metadata
        if track_meta['filepath'] == '' and basefolder is None:
            filepath = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{track_meta['provider']}/{track_meta['albumartist']}/{track_meta['album']}"
        else:
            filepath = basefolder
        
    raw_data = await qobuz_api.get_track_url(item_id)
    try:
        url = raw_data['url']
    except KeyError:
        return await send_message(user, lang.s.ERR_QOBUZ_NOT_AVAILABLE)
        
    track_meta['extension'], track_meta['quality'] = await get_quality(raw_data)

    # add filename to filepath
    filename = await format_string(Config.TRACK_NAME_FORMAT, track_meta, user)
    filepath += f"/{filename}.{track_meta['extension']}"
    filepath = sanitize_filepath(filepath)
    track_meta['filepath'] = filepath

    err = await download_file(url, filepath)
    if err:
        return await send_message(user, err)
    
    await set_metadata(track_meta)

    if upload:
        await track_upload(track_meta, user, disable_link)
            
    # Acknowledge task finished
    return True



async def start_artist(albums, user, artist):
    artist_meta = await get_artist_meta(artist[0])
    artist_meta['folderpath'] = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/Qobuz/{artist[0]['name']}"
    artist_meta['folderpath'] = sanitize_filepath(artist_meta['folderpath'])

    upload_album = True
    if bot_set.artist_batch:
        # for telegram, batch upload is not needed
        upload_album = True if bot_set.upload_mode == 'Telegram' else False
    if bot_set.artist_zip:
        upload_album = False # final decision

    # no concurrent download
    for album in albums:
        await start_album(album['id'], user, upload_album, artist_meta['folderpath'])

    # now upload artist folder as a whole
    if not upload_album:
        if bot_set.artist_zip:
            await edit_message(user['bot_msg'], lang.s.ZIPPING)
            artist_meta['folderpath'] = await zip_handler(artist_meta['folderpath'])
        
        await edit_message(user['bot_msg'], lang.s.UPLOADING)
        await artist_upload(artist_meta, user)



async def start_playlist(tracks, playlist, user):
    play_meta = await get_playlist_meta(playlist[0], tracks)
    
    playlist_folder = None

    # temp variable (telegram upload doesnt need sorting)
    playlist_sort = False if bot_set.upload_mode == 'Telegram' else bot_set.playlist_sort
    
    if not playlist_sort:
        playlist_folder = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/Qobuz/{play_meta['title']}"
        playlist_folder = sanitize_filepath(playlist_folder)
    play_meta['folderpath'] = playlist_folder
    
    # Get user quality by doing a track request
    track_meta = await qobuz_api.get_track_url(tracks[0]['id'])
    _, play_meta['quality'] = await get_quality(track_meta)

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

    if bot_set.playlist_zip:
        await edit_message(user['bot_msg'], lang.s.ZIPPING)
        if playlist_sort:
            play_meta['folderpath'] = await move_sorted_playlist(play_meta, user)
        play_meta['folderpath'] = await zip_handler(play_meta['folderpath'])
       
    if not upload:
        await edit_message(user['bot_msg'], lang.s.UPLOADING)
        await playlist_upload(play_meta, user)
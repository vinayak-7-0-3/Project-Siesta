import json
import base64

from pathvalidate import sanitize_filepath

from .tidal_api import tidalapi
from .utils import *
from .metadata import get_track_metadata

from ..utils import *
from ..metadata import set_metadata, get_audio_extension
from ..uploder import *
from ..message import send_message

from bot.logger import LOGGER
from config import Config


async def start_tidal(url:str, user:dict):
    item_id, type_ = await parse_url(url)

    if type_ == 'track':
        await start_track(item_id, user)
    elif type_ == 'artist':
        pass
    elif type_ == 'album':
        pass
    elif type_ == 'playlist':
        pass
    else:
        await send_message(user, "Invalid Tidal URL")
        

async def start_track(track_id:int, user:dict, upload=True):
    track_data = await tidalapi.get_track(track_id)
    track_meta = await get_track_metadata(track_id, track_data)
    media_tags, format = await get_media_tags(track_data)

    session = {
            'flac_hires': tidalapi.mobile_hires,
            '360ra': tidalapi.mobile_hires if tidalapi.mobile_hires else tidalapi.mobile_atmos,
            'ac4': tidalapi.mobile_atmos,
            'ac3': tidalapi.tv_session,
            None: tidalapi.tv_session,
    }[format]

    # tv sesion gets atmos always so try mobi1e session if exists
    if not format and 'DOLBY_ATMOS' in media_tags:
        if tidalapi.mobile_hires:
            session = tidalapi.mobile_hires

    quality = tidalapi.quality if format != 'flac_hires' else 'HI_RES_LOSSLESS'
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
        if stream_data['manifestMimeType'] == 'application/dash+xml':
            manifest = base64.b64decode(stream_data['manifest'])
            urls, track_codec = parse_mpd(manifest)
        else:
            manifest = json.loads(base64.b64decode(stream_data['manifest']))
            track_codec = 'AAC' if 'mp4a' in manifest['codecs'] else manifest['codecs'].upper()
            urls = manifest['urls'][0]

        filepath = f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/{track_meta['provider']}/{track_meta['albumartist']}/{track_meta['album']}"
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

        
    
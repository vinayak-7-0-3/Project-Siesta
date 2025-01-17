import os

from mutagen import File
from config import Config
from mutagen import flac, mp4
from mutagen.mp3 import EasyMP3
from mutagen.id3 import TALB, TCOP, TDRC, TIT2, TPE1, TRCK, APIC, \
    TCON, TOPE, TSRC, USLT, TPOS, TXXX

from bot.logger import LOGGER
from .utils import download_file


metadata = {
        'itemid': '',
        'copyright': '',
        'albumartist': '',
        'cover': '',
        'thumbnail': '',
        'artist': '',
        'upc': '',
        'album': '',
        'isrc': '',
        'title': '',
        'duration': '',
        'explicit': '',
        "tracknumber": '',
        'date': '',
        'totaltracks': '',
        'quality': '',
        'extension': '',
        'lyrics': '',
        'volume': '',
        'totalvolume': '',
        'genre': '',
        'provider': '',
        'tracks': [],
        'albums': [],
        'tempfolder': f'{Config.DOWNLOAD_BASE_DIR}/', # specific folder for each user
        'filepath': '',   # if track, full path to file
        'folderpath': '', # if album/playlist the full path to folder
        'poster_msg': None,  # Pyrogram message of post (if exist)
        'type': ''       # track/album/playlist/artist
    }


async def set_metadata(metadata:dict):
    audio_path = metadata['filepath']

    handle = File(audio_path)

    if metadata['duration'] == '':
        metadata['duration'] = handle.info.length

    if 'audio/x-flac' in handle.mime:
        await set_flac(metadata, handle)
    elif 'audio/mpeg' in handle.mime:
        await set_mp3(metadata, handle)
    elif 'audio/x-m4a' in handle.mime: 
        await set_m4a(metadata, handle)


async def set_flac(data, handle):
    if handle.tags is None:
            handle.add_tags()
    handle.tags['title'] = data['title']
    handle.tags['album'] = data['album']
    handle.tags['albumartist'] = data['albumartist']
    handle.tags['artist'] = data['artist']
    handle.tags['copyright'] = data['copyright']
    handle.tags['tracknumber'] = str(data['tracknumber'])
    handle.tags['tracktotal'] = str(data['totaltracks'])
    handle.tags['genre'] = data['genre']
    handle.tags['date'] = data['date']
    handle.tags['isrc'] = data['isrc']
    handle.tags['lyrics'] = data['lyrics']
    await savePic(handle, data)
    handle.save()
    return True

async def set_mp3(data, handle):
    # ID3
    if handle.tags is None:
            handle.add_tags()
    handle.tags.add(TIT2(encoding=3, text=data['title']))
    handle.tags.add(TALB(encoding=3, text=data['album']))
    handle.tags.add(TOPE(encoding=3, text=data['albumartist']))
    handle.tags.add(TPE1(encoding=3, text=data['artist']))
    handle.tags.add(TCOP(encoding=3, text=data['copyright']))
    handle.tags.add(TRCK(encoding=3, text=str(data['tracknumber'])))
    handle.tags.add(TPOS(encoding=3, text=str(data['volume'])))
    handle.tags.add(TXXX(encoding=3, text=str(data['totaltracks'])))
    handle.tags.add(TCON(encoding=3, text=data['genre']))
    handle.tags.add(TDRC(encoding=3, text=data['date']))
    handle.tags.add(TSRC(encoding=3, text=data['isrc']))
    handle.tags.add(USLT(encoding=3, lang=u'eng', desc=u'desc', text=data['lyrics']))
    await savePic(handle, data)
    handle.save()
    return True

async def set_m4a(data, handle):
    if handle.tags is None:
        handle.add_tags()
    handle.tags['\u00a9nam'] = data['title']
    handle.tags['\u00a9alb'] = data['album']
    handle.tags['\u00a9ART'] = data['artist']
    handle.tags['aART'] = data['albumartist']
    handle.tags['\u00a9day'] = data['date']
    handle.tags['\u00a9gen'] = data['genre']
    handle.tags['\u00a9cpr'] = data['copyright']

    track_number = int(data['tracknumber']) if data['tracknumber'] != '' else 0
    totaltracks = int(data['totaltracks']) if data['totaltracks'] != '' else 0
    handle.tags['trkn'] = [(track_number, totaltracks)]
    volume = int(data['volume']) if data['volume'] != '' else 0
    totalvolume = int(data['totalvolume']) if data['totalvolume'] != '' else 0
    handle.tags['disk'] = [(volume, totalvolume)]


    await savePic(handle, data)
    handle.save()
    return True


async def savePic(handle, metadata):
    album_art = metadata['cover']

    try:
        with open(album_art, "rb") as f:
            data = f.read()
    except Exception as e:
        await LOGGER.error(e)
        return

    if 'audio/x-flac' in handle.mime:
        pic = flac.Picture()
        pic.data = data
        pic.mime = u"image/jpeg"
        handle.clear_pictures()
        handle.add_picture(pic)

    if 'audio/mpeg' in handle.mime:
        handle.tags.add(APIC(encoding=3, data=data))

    if 'audio/x-m4a' in handle.mime:
        pic = mp4.MP4Cover(data)
        handle.tags['covr'] = [pic]

    if 'audio/ogg' in handle.mime:
        handle['artwork'] = data



async def get_audio_extension(path):
    handle = File(path)
    
    if 'audio/x-m4a' in handle.mime:
        return 'm4a'
    elif 'audio/x-flac' in handle.mime:
        return 'flac'
    else:
        return 'mp3'


async def create_cover_file(url:dict, meta:dict, thumbnail=False):
    filename = f"{meta['itemid']}-thumb.jpg" if thumbnail else f"{meta['itemid']}.jpg"
    cover = meta['tempfolder'] + filename
    
    if not os.path.exists(cover):
        err = await download_file(url, cover, 1, 5)
        if err:
            return './project-siesta.png'
    return cover
import copy

from datetime import datetime

from ..metadata import metadata as base_meta
from ..metadata import create_cover_file
from .dzapi import deezerapi



async def process_track_metadata(track_id, r_id, cover=None, \
    thumbnail=False):
    metadata = copy.deepcopy(base_meta)

    raw_meta = await deezerapi.get_track(track_id)
    raw_meta=raw_meta['DATA']
    t_meta = raw_meta.get('FALLBACK', raw_meta)
    
    metadata['tempfolder'] += f"{r_id}-temp/"

    metadata['itemid'] = track_id
    metadata['copyright'] = t_meta.get('COPYRIGHT', '')
    metadata['albumartist'] = t_meta['ART_NAME']
    metadata['artist'] = get_artists_name(t_meta)
    metadata['album'] = t_meta['ALB_TITLE']
    metadata['isrc'] = t_meta['ISRC']

    metadata['title'] = t_meta['SNG_TITLE']
    if t_meta.get('VERSION'):
        metadata['title'] += f' ({t_meta["VERSION"]})'

    # title might have '/' in it
    metadata['title'] = metadata['title'].replace('/', ' ')

    metadata['duration'] = t_meta['DURATION']
    #metadata['explicit'] = t_meta['EXPLICIT_TRACK_CONTENT']['EXPLICIT_LYRICS_STATUS']
    metadata['tracknumber'] = t_meta['TRACK_NUMBER']

    metadata['date'] = t_meta.get('PHYSICAL_RELEASE_DATE', '')

    metadata['provider'] = 'Deezer'
    metadata['type'] = 'track'

    # reuse albumart if possible
    metadata['cover'] = cover if cover else await get_cover(t_meta['ALB_PICTURE'], metadata)
    metadata['thumbnail'] = thumbnail if thumbnail else await get_cover(t_meta['ALB_PICTURE'], metadata, True)

    metadata['token'] = t_meta['TRACK_TOKEN']
    metadata['token_expiry'] = t_meta['TRACK_TOKEN_EXPIRE']

    metadata['quality'] = await get_quality(t_meta)

    return metadata
            

async def process_album_metadata(album_id:int, a_meta:dict, t_meta:list, r_id):
    metadata = copy.deepcopy(base_meta)

    metadata['tempfolder'] += f"{r_id}-temp/"

    metadata['itemid'] = album_id

    metadata['albumartist'] = a_meta['ART_NAME']
    metadata['upc'] = a_meta['UPC']
    metadata['title'] = a_meta['ALB_TITLE']
    if a_meta.get('VERSION'):
        metadata['title'] += f' ({a_meta['VERSION']})'
    metadata['album'] = a_meta['ALB_TITLE']
    metadata['artist'] = get_artists_name(a_meta)
    metadata['date'] = a_meta['DIGITAL_RELEASE_DATE']
    metadata['totaltracks'] = a_meta['NUMBER_TRACK']
    metadata['duration'] = a_meta['DURATION']
    metadata['copyright'] = a_meta['COPYRIGHT']
    #metadata['explicit'] = a_meta['explicit']
    #metadata['totalvolume'] = a_meta['numberOfVolumes']
    metadata['provider'] = 'Deezer'
    metadata['type'] = 'album'

    metadata['cover'] = await get_cover(a_meta['ALB_PICTURE'], metadata)
    metadata['thumbnail'] = await get_cover(a_meta['ALB_PICTURE'], metadata, True)
        
    #metadata['quality'] = await get_quality(t_meta['data'][0])

    metadata['tracks'] = []
    for track in t_meta['data']:
        track_meta = await process_track_metadata(
            track['SNG_ID'], 
            r_id,
            metadata['cover'], 
            metadata['thumbnail']
        )
        metadata['tracks'].append(track_meta)

    metadata['quality'] = metadata['tracks'][0]['quality']
    
    return metadata



async def process_playlist_meta(raw_meta, r_id):
    metadata = copy.deepcopy(base_meta)

    metadata['tempfolder'] += f"{r_id}-temp/"

    metadata['title'] = raw_meta['DATA']['TITLE']
    metadata['duration'] = raw_meta['DATA']['DURATION']
    metadata['totaltracks'] = raw_meta['DATA']['NB_SONG']
    metadata['itemid'] = raw_meta['DATA']['PLAYLIST_ID']
    metadata['type'] = 'playlist'
    metadata['provider'] = 'Deezer'
    metadata['cover'] = await get_cover(raw_meta['DATA']['PLAYLIST_PICTURE'], metadata)
    metadata['thumbnail'] = await get_cover(raw_meta['DATA']['PLAYLIST_PICTURE'], metadata, True)
    
    for track in raw_meta['SONGS']['data']:
        track_meta = await process_track_metadata(track['SNG_ID'], r_id)
        metadata['tracks'].append(track_meta)

    metadata['quality'] = metadata['tracks'][0]['quality']

    return metadata








def get_artists_name(meta:dict):
    artists = []
    for a in meta['ARTISTS']:
        artists.append(a['ART_NAME'])
    return ', '.join([str(artist) for artist in artists])


async def get_cover(cover_id, meta:dict, thumbnail=False):
    url = None
    if cover_id:
        url = (
            f'https://cdn-images.dzcdn.net/images/cover/{cover_id}/3000x0-none-100-0-0.png'
            if not thumbnail
            else f'https://cdn-images.dzcdn.net/images/cover/{cover_id}/80x0-none-100-0-0.png'
        )
    return await create_cover_file(url, meta, thumbnail)


async def get_quality(meta:dict):
    format = 'FLAC'
    premium_formats = ['FLAC', 'MP3_320']
    countries = meta.get('AVAILABLE_COUNTRIES', {}).get('STREAM_ADS')
    
    if not countries:
        raise Exception("Deezer : Track not available")
    elif deezerapi.country not in countries:
        raise Exception("Deezer : Track not available in your country")
    else:
        formats_to_check = premium_formats
        while len(formats_to_check) != 0:
            if formats_to_check[0] != format:
                formats_to_check.pop(0)
            else:
                break

        temp_f = None
        for f in formats_to_check:
            if meta[f'FILESIZE_{f}'] != '0':
                temp_f = f
                break
        if temp_f is None:
            temp_f = 'MP3_128'
        format = temp_f

        if format not in deezerapi.available_formats:
            raise Exception("Deezer : Format not available by your subscription")

    return format
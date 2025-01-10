import copy

from datetime import datetime

from ..metadata import metadata as base_meta
from ..metadata import create_cover_file



async def get_track_metadata(track_id, t_meta, r_id, cover=None, thumbnail=False):
    """
    Args:
        item_id : track id
        t_meta : raw metadata from tidal (pre-fetched)
    Returns:
        metadata: dict
    """

    metadata = copy.deepcopy(base_meta)

    metadata['tempfolder'] += f"{r_id}-temp/"

    metadata['itemid'] = track_id
    metadata['copyright'] = t_meta['copyright']
    metadata['albumartist'] = t_meta['artist']['name']
    metadata['artist'] = get_artists_name(t_meta)
    metadata['album'] = t_meta['album']['title']
    metadata['isrc'] = t_meta['isrc']

    metadata['title'] = t_meta['title']
    if t_meta['version']:
        metadata['title'] += f' ({t_meta["version"]})'

    # title might have '/' in it
    metadata['title'] = metadata['title'].replace('/', ' ')

    metadata['duration'] = t_meta['duration']
    metadata['explicit'] = t_meta['explicit']
    metadata['tracknumber'] = t_meta['trackNumber']

    parsed_date = datetime.strptime(t_meta['streamStartDate'], '%Y-%m-%dT%H:%M:%S.%f%z')
    metadata['date'] = str(parsed_date.date())

    metadata['provider'] = 'Tidal'
    metadata['type'] = 'track'

    # reuse albumart if possible
    metadata['cover'] = cover if cover else await get_cover(t_meta['album'].get('cover'), metadata)
    metadata['thumbnail'] = thumbnail if thumbnail else await get_cover(t_meta['album'].get('cover'), metadata, True)

    return metadata


async def get_album_metadata(album_id, a_meta, t_meta, r_id):
    metadata = copy.deepcopy(base_meta)

    metadata['tempfolder'] += f"{r_id}-temp/"

    metadata['itemid'] = album_id
    metadata['albumartist'] = a_meta['artist']['name']
    metadata['upc'] = a_meta['upc']
    metadata['title'] = a_meta['title']
    if a_meta['version']:
        metadata['title'] += f' ({a_meta["version"]})'
    metadata['album'] = a_meta['title']
    metadata['artist'] = get_artists_name(a_meta)
    metadata['date'] = a_meta['releaseDate']
    metadata['totaltracks'] = a_meta['numberOfTracks']
    metadata['duration'] = a_meta['duration']
    metadata['copyright'] = a_meta['copyright']
    metadata['explicit'] = a_meta['explicit']
    metadata['totalvolume'] = a_meta['numberOfVolumes']
    metadata['provider'] = 'Tidal'
    metadata['type'] = 'album'

    metadata['cover'] = await get_cover(a_meta.get('cover'), metadata)
    metadata['thumbnail'] = await get_cover(a_meta.get('cover'), metadata, True)


    metadata['tracks'] = []
    for track in t_meta['items']:
        track_meta = await get_track_metadata(track['id'], track, r_id, metadata['cover'], metadata['thumbnail'])
        metadata['tracks'].append(track_meta)
    
    return metadata


async def get_artist_metadata(a_meta:dict, r_id):
    metadata = copy.deepcopy(base_meta)

    metadata['tempfolder'] += f"{r_id}-temp/"

    metadata['artist'] = a_meta['name']
    metadata['title'] = a_meta['name']
    metadata['provider'] = 'Tidal'
    metadata['type'] = 'artist'
    metadata['cover'] = await get_cover(a_meta.get('picture'), metadata)
    metadata['thumbnail'] = await get_cover(a_meta.get('picture'), metadata, True)
    return metadata


async def get_cover(cover_id, meta:dict, thumbnail=False):
    url = None
    if cover_id:
        url = (
            f'https://resources.tidal.com/images/{cover_id.replace("-", "/")}/80x80.jpg'
            if thumbnail
            else f'https://resources.tidal.com/images/{cover_id.replace("-", "/")}/origin.jpg'
        )
    return await create_cover_file(url, meta, thumbnail)


def get_artists_name(meta:dict):
    artists = []
    for a in meta['artists']:
        artists.append(a['name'])
    return ', '.join([str(artist) for artist in artists])
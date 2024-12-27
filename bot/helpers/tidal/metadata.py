import copy

from datetime import datetime

from ..metadata import metadata as base_meta



async def get_track_metadata(track_id, t_meta):
    """
    Args:
        item_id : track id
        t_meta : raw metadata from tidal (pre-fetched)
    Returns:
        metadata: dict
    """

    metadata = copy.deepcopy(base_meta)

    metadata['itemid'] = track_id
    metadata['copyright'] = t_meta['copyright']
    metadata['albumartist'] = t_meta['artist']['name']
    metadata['cover'] = get_cover_url(t_meta['album'].get('cover'))
    metadata['thumbnail'] = get_cover_url(t_meta['album'].get('cover'))
    metadata['artist'] = get_artists_name(t_meta)
    metadata['album'] = t_meta['album']['title']
    metadata['isrc'] = t_meta['isrc']
    metadata['title'] = t_meta['title']
    metadata['duration'] = t_meta['duration']
    metadata['explicit'] = t_meta['explicit']
    metadata['tracknumber'] = t_meta['trackNumber']

    parsed_date = datetime.strptime(t_meta['streamStartDate'], '%Y-%m-%dT%H:%M:%S.%f%z')
    metadata['date'] = str(parsed_date.date())

    metadata['provider'] = 'Tidal'
    metadata['type'] = 'track'

    return metadata




def get_cover_url(cover_id, thumbnail=False):
    if cover_id:
        if thumbnail:
            return f'https://resources.tidal.com/images/{cover_id.replace("-", "/")}/80x80.jpg'
        return f'https://resources.tidal.com/images/{cover_id.replace("-", "/")}/origin.jpg'
    else:
        return './project-siesta.png'


def get_artists_name(meta:dict):
    artists = []
    for a in meta['artists']:
        artists.append(a['name'])
    return ', '.join([str(artist) for artist in artists])
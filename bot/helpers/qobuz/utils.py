# From vitiko98/qobuz-dl
import re

from .qopy import qobuz_api
from ..translations import lang
from ..message import send_message, edit_message
from ..utils import format_string
from ..metadata import metadata as base_meta

from bot.settings import bot_set



async def get_track_metadata(item_id, q_meta=None):
    """
    Args:
        item_id : track id
        q_meta : raw metadata from qobuz (pre-fetched)
    """
    if q_meta is None:
        raw_meta = await qobuz_api.get_track_url(item_id)
        if "sample" not in raw_meta and raw_meta.get('sampling_rate'):
            q_meta = await qobuz_api.get_track_meta(item_id)
            if not q_meta.get('streamable'):
                return None, lang.ERR_QOBUZ_NOT_STREAMABLE
        else:
            return None, lang.ERR_QOBUZ_NOT_STREAMABLE
    
    metadata = base_meta.copy()
    metadata['itemid'] = item_id
    metadata['copyright'] = q_meta['copyright']
    metadata['albumartist'] = q_meta['album']['artist']['name']
    metadata['cover'] = q_meta['album']['image']['large']
    metadata['thumbnail'] = q_meta['album']['image']['thumbnail']
    metadata['artist'] = await get_artists_name(q_meta['album'])
    metadata['upc'] = q_meta['album']['upc']
    metadata['album'] = q_meta['album']['title']
    metadata['isrc'] = q_meta['isrc']
    metadata['title'] = q_meta['title']
    metadata['duration'] = q_meta['duration']
    metadata['explicit'] = q_meta['parental_warning']
    metadata['tracknumber'] = q_meta['track_number']
    metadata['date'] = q_meta['release_date_original']
    metadata['totaltracks'] = q_meta['album']['tracks_count']
    metadata['provider'] = 'Qobuz'
    metadata['type'] = 'track'

    return metadata, None  
        
async def get_album_metadata(item_id):
    q_meta = await qobuz_api.get_album_meta(item_id)
    if not q_meta.get('streamable'):
        return None, lang.ERR_QOBUZ_NOT_STREAMABLE
    
    metadata = base_meta.copy()
    metadata['itemid'] = item_id
    metadata['albumartist'] = q_meta['artist']['name']
    metadata['upc'] = q_meta['upc']
    metadata['title'] = q_meta['title']
    metadata['album'] = q_meta['title']
    metadata['artist'] = q_meta['artist']['name']
    metadata['date'] = q_meta['release_date_original']
    metadata['totaltracks'] = q_meta['tracks_count']
    metadata['cover'] = q_meta['image']['large']
    metadata['thumbnail'] = q_meta['image']['thumbnail']
    metadata['duration'] = q_meta['duration']
    metadata['copyright'] = q_meta['copyright']
    metadata['genre'] = q_meta['genre']['name']
    metadata['explicit'] = q_meta['parental_warning']
    metadata['provider'] = 'Qobuz'
    metadata['tracks'] = await get_track_meta_from_alb(q_meta, metadata)
    metadata['type'] = 'album'

    return metadata, None

async def get_track_meta_from_alb(q_meta:dict, alb_meta):
    """
    q_meta : raw metadata from qobuz (album)
    alb_meta : Sorted metadata (album)
    """
    tracks = []
    for track in q_meta['tracks']['items']:
        metadata = alb_meta.copy()
        metadata['itemid'] = track['id']
        metadata['title'] = track['title']
        metadata['duration'] = track['duration']
        metadata['isrc'] = track['isrc']
        metadata['tracknumber'] = track['track_number']
        metadata['tracks'] = ''
        metadata['type'] = 'track'
        tracks.append(metadata)
    return tracks


async def get_playlist_meta(raw_meta, tracks):
    """
    Args:
        raw_meta : raw metadata of playlist from qobuz
        tracks : list of tracks (raw metadata)
    """
    metadata = base_meta.copy()
    metadata['title'] = raw_meta['name']
    metadata['duration'] = raw_meta['duration']
    metadata['totaltracks'] = raw_meta['tracks_count']
    metadata['itemid'] = raw_meta['id']
    metadata['type'] = 'playlist'
    
    for track in tracks:
        track_meta, _ = await get_track_metadata(track['id'], track)
        metadata['tracks'].append(track_meta)
    return metadata

async def get_artist_meta(artist_raw):
    """
    Args:
        artist_raw : raw metadata of artist from qobuz
    """
    metadata = base_meta.copy()
    metadata['title'] = artist_raw['name']
    metadata['type'] = 'artist'
    metadata['provider'] = 'Qobuz'
    return metadata

async def get_artists_name(meta):
    artists = []
    try:
        for a in meta['artists']:
            artists.append(a['name'])
    except:
        artists.append(meta['artist']['name'])
    return ', '.join([str(artist) for artist in artists])


async def check_type(url):
    possibles = {
            "playlist": {
                "func": qobuz_api.get_plist_meta,
                "iterable_key": "tracks",
            },
            "artist": {
                "func": qobuz_api.get_artist_meta,
                "iterable_key": "albums",
            },
            "interpreter": {
                "func": qobuz_api.get_artist_meta,
                "iterable_key": "albums",
            },
            "label": {
                "func": qobuz_api.get_label_meta,
                "iterable_key": "albums",
            },
            "album": {"album": True, "func": None, "iterable_key": None},
            "track": {"album": False, "func": None, "iterable_key": None},
        }
    try:
        url_type, item_id = await get_url_info(url)
        type_dict = possibles[url_type]
    except (KeyError, IndexError):
        return

    content = None
    if type_dict["func"]:
        res = await type_dict["func"](item_id)
        content = [item for item in res]

        smart_discography = True
        if smart_discography and url_type == "artist":
            # change `save_space` and `skip_extras` for customization
            items = smart_discography_filter(
                content,
                save_space=True,
                skip_extras=True,
            )
        else:
            items = [item[type_dict["iterable_key"]]["items"] for item in content][
                0
            ]
            
        return items, None, type_dict, content
    else:
        return None, item_id, type_dict, content


async def get_url_info(url):
    r = re.search(
        r"(?:https:\/\/(?:w{3}|open|play)\.qobuz\.com)?(?:\/[a-z]{2}-[a-z]{2})"
        r"?\/(album|artist|track|playlist|label|interpreter)(?:\/[-\w\d]+)?\/([\w\d]+)",
        url,
    )
    return r.groups()


def smart_discography_filter(
    contents: list, save_space: bool = False, skip_extras: bool = False
) -> list:

    TYPE_REGEXES = {
        "remaster": r"(?i)(re)?master(ed)?",
        "extra": r"(?i)(anniversary|deluxe|live|collector|demo|expanded)",
    }

    def is_type(album_t: str, album: dict) -> bool:
        """Check if album is of type `album_t`"""
        version = album.get("version", "")
        title = album.get("title", "")
        regex = TYPE_REGEXES[album_t]
        return re.search(regex, f"{title} {version}") is not None

    def essence(album: dict) -> str:
        """Ignore text in parens/brackets, return all lowercase.
        Used to group two albums that may be named similarly, but not exactly
        the same.
        """
        r = re.match(r"([^\(]+)(?:\s*[\(\[][^\)][\)\]])*", album)
        return r.group(1).strip().lower()

    requested_artist = contents[0]["name"]
    items = [item["albums"]["items"] for item in contents][0]

    # use dicts to group duplicate albums together by title
    title_grouped = dict()
    for item in items:
        title_ = essence(item["title"])
        if title_ not in title_grouped:  # ?
            #            if (t := essence(item["title"])) not in title_grouped:
            title_grouped[title_] = []
        title_grouped[title_].append(item)

    items = []
    for albums in title_grouped.values():
        best_bit_depth = max(a["maximum_bit_depth"] for a in albums)
        get_best = min if save_space else max
        best_sampling_rate = get_best(
            a["maximum_sampling_rate"]
            for a in albums
            if a["maximum_bit_depth"] == best_bit_depth
        )
        remaster_exists = any(is_type("remaster", a) for a in albums)

        def is_valid(album: dict) -> bool:
            return (
                album["maximum_bit_depth"] == best_bit_depth
                and album["maximum_sampling_rate"] == best_sampling_rate
                and album["artist"]["name"] == requested_artist
                and not (  # states that are not allowed
                    (remaster_exists and not is_type("remaster", album))
                    or (skip_extras and is_type("extra", album))
                )
            )

        filtered = tuple(filter(is_valid, albums))
        # most of the time, len is 0 or 1.
        # if greater, it is a complete duplicate,
        # so it doesn't matter which is chosen
        if len(filtered) >= 1:
            items.append(filtered[0])

    return items

    
async def get_quality(meta:dict):
    """
    Args
        meta : track url metadata dict
    Returns
        extention, quality
    """
    if qobuz_api.quality == 5:
        return 'mp3', '320K'
    else:
        return 'flac', f'{meta["bit_depth"]}B - {meta["sampling_rate"]}k'
import re

from shutil import copyfileobj
from xml.etree import ElementTree

from .tidal_api import tidalapi


async def parse_url(url):
    """
    Parse url type and ID from Tidal URL
    Args:
        url (str): Tidal URL.
    Returns:
        id: int
        type: str
    """
    patterns = [
        (r"/browse/track/(\d+)", "track"),  # Track from browse
        (r"/browse/artist/(\d+)", "artist"),  # Artist from browse
        (r"/browse/album/(\d+)", "album"),  # Album from browse
        (r"/browse/playlist/([\w-]+)", "playlist"),  # Playlist with numeric or UUID
        (r"/track/(\d+)", "track"),  # Track from listen.tidal.com
        (r"/artist/(\d+)", "artist"),  # Artist from listen.tidal.com
        (r"/playlist/([\w-]+)", "playlist"),  # Playlist with numeric or UUID
        (r"/album/\d+/track/(\d+)", "track")  # Extract only track ID from album_and_track
    ]
    
    for pattern, type_ in patterns:
        match = re.search(pattern, url)
        if match:
            #return {"type": type_, "id": match.group(1)}
            return match.group(1), type_
    
    return None, None


async def get_media_tags(json_resp: dict):
    """
    Get media tags and format from Tidal response
    Args:
        json_resp (dict): Tidal response.
    Returns:
        list: Media tags.
        format: str
    """
    media_tags = json_resp['mediaMetadata']['tags']

    format = None

    if tidalapi.spatial == 'Sony 360RA':
        if 'SONY_360RA' in media_tags:
            format = '360ra'
    elif tidalapi.spatial == 'ATMOS AC3 JOC':
        if 'DOLBY_ATMOS' in media_tags:
            format = 'ac3'
    elif tidalapi.spatial == 'ATMOS AC4':
        if 'DOLBY_ATMOS' in media_tags:
            format = 'ac4'
    # let spatial audio have priority
    elif 'HIRES_LOSSLESS' in media_tags and not format and tidalapi.quality == 'HI_RES':
        format = 'flac_hires'

    return media_tags, format
    


def parse_mpd(xml: bytes) -> list:
    xml = xml.decode('UTF-8')
    # Removes default namespace definition, don't do that!
    xml = re.sub(r'xmlns="[^"]+"', '', xml, count=1)
    root = ElementTree.fromstring(xml)

    # List of AudioTracks
    tracks = []

    for period in root.findall('Period'):
        for adaptation_set in period.findall('AdaptationSet'):
            for rep in adaptation_set.findall('Representation'):
                # Check if representation is audio
                content_type = adaptation_set.get('contentType')
                if content_type != 'audio':
                    raise ValueError('Only supports audio MPDs!')

                # Codec checks
                codec = rep.get('codecs').upper()
                if codec.startswith('MP4A'):
                    codec = 'AAC'

                # Segment template
                seg_template = rep.find('SegmentTemplate')
                # Add init file to track_urls
                track_urls = [seg_template.get('initialization')]
                start_number = int(seg_template.get('startNumber') or 1)

                # https://dashif-documents.azurewebsites.net/Guidelines-TimingModel/master/Guidelines-TimingModel.html#addressing-explicit
                # Also see example 9
                seg_timeline = seg_template.find('SegmentTimeline')
                if seg_timeline is not None:
                    seg_time_list = []
                    cur_time = 0

                    for s in seg_timeline.findall('S'):
                        # Media segments start time
                        if s.get('t'):
                            cur_time = int(s.get('t'))

                        # Segment reference
                        for i in range((int(s.get('r') or 0) + 1)):
                            seg_time_list.append(cur_time)
                            # Add duration to current time
                            cur_time += int(s.get('d'))

                    # Create list with $Number$ indices
                    seg_num_list = list(range(start_number, len(seg_time_list) + start_number))
                    # Replace $Number$ with all the seg_num_list indices
                    track_urls += [seg_template.get('media').replace('$Number$', str(n)) for n in seg_num_list]

                tracks.append(track_urls)

    return tracks, codec


async def merge_tracks(temp_tracks:list, output_path:str):
    with open(output_path, 'wb') as dest_file:
        for temp_location in temp_tracks:
            with open(temp_location, 'rb') as segment_file:
                copyfileobj(segment_file, dest_file)
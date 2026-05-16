import re
import asyncio

from urllib.parse import urlparse

from bot import LOGGER
from bot.models.provider import Provider

from bot.providers.deezer.deezer_api import deezerapi
from bot.providers.deezer.metadata import DeezerMetadata
from bot.providers.deezer.errors import TrackNotAvailable, InvalidURL

from bot.utils.message import send_text
from bot.utils.metadata import set_metadata


class DeezerHandler(Provider):

    @staticmethod
    async def _parse_url_async(url):
        url = urlparse(url)

        path_match = re.match(
            r'^\/(?:[a-z]{2}\/)?(track|album|artist|playlist)\/(\d+)\/?$',
            url.path
        )

        if not path_match:
            raise InvalidURL(f'DEEZER : Invalid URL: {url}')

        return int(path_match.group(2)), path_match.group(1)


    @staticmethod
    def parse_url(url):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop → safe to run
            return asyncio.run(DeezerHandler._parse_url_async(url))
        else:
            # Already in async context → caller must await
            raise RuntimeError(
                "parse_url() called from async context. Use await parse_url_async()."
            )



    @classmethod
    async def get_track_metadata(cls, item_id, task_details):
        raw_data = await deezerapi.get_track(item_id)
        
        track_data = raw_data['DATA']
        track_data = track_data.get('FALLBACK', track_data)
        
        metadata = await DeezerMetadata.process_track_metadata(
            item_id,
            track_data,
            task_details.tempfolder
        )
        
        return metadata


    @classmethod
    async def get_album_metadata(cls, item_id: str, task_details):
        raw_data = await deezerapi.get_album(item_id)
        
        album_data = raw_data['DATA']
        track_datas = raw_data['SONGS']['data']
        
        metadata = await DeezerMetadata.process_album_metadata(
            item_id,
            album_data,
            track_datas,
            task_details.tempfolder
        )
        
        return metadata


    @classmethod
    async def get_artist_metadata(cls, item_id, task_details):
        raw_data = await deezerapi.get_artist(item_id)
        
        artist_data = raw_data['DATA']
        
        album_ids = await deezerapi.get_artist_album_ids(item_id, 0, -1, False)
        
        albums = []
        for album_id in album_ids:
            try:
                album_metadata = await cls.get_album_metadata(str(album_id), task_details)
                albums.append(album_metadata)
            except Exception as e:
                LOGGER.error(f"DEEZER: Failed to get album {album_id}: {e}")
                continue
        
        metadata = await DeezerMetadata.process_artist_metadata(
            artist_data,
            albums,
            task_details.tempfolder
        )
        
        return metadata


    @classmethod
    async def get_playlist_metadata(cls, item_id, task_details):
        raw_data = await deezerapi.get_playlist(item_id)
        
        playlist_data = raw_data['DATA']
        track_datas = raw_data['SONGS']['data']
        
        tracks = []
        for track in track_datas:
            try:
                track_meta = await DeezerMetadata.process_track_metadata(
                    track['SNG_ID'],
                    track,
                    task_details.tempfolder
                )
                tracks.append(track_meta)
            except TrackNotAvailable:
                LOGGER.error(f"DEEZER: Track not available in playlist - {playlist_data.get('TITLE', '')}")
                continue
            except Exception as e:
                LOGGER.error(f"DEEZER: Failed to process track in playlist: {e}")
                continue
        
        metadata = await DeezerMetadata.process_playlist_metadata(
            playlist_data,
            tracks,
            task_details.tempfolder
        )
        
        return metadata


    @classmethod
    async def download_track(cls, metadata, task_details, download_path):
        track_token = metadata._extra.get('token')
        track_token_expiry = metadata._extra.get('token_expiry')
        quality = metadata._extra.get('quality', 'MP3_128')
        
        try:
            url = await deezerapi.get_track_url(
                metadata.itemid,
                track_token,
                track_token_expiry,
                quality
            )
        except Exception as e:
            LOGGER.error(f"DEEZER: Failed to get track URL: {e}")
            await send_text(str(e), task_details)
            return None
        
        extension = 'flac' if quality == 'FLAC' else 'mp3'
        metadata.extension = extension
        metadata.quality = quality
        
        download_path = download_path.with_suffix(f".{extension}")
        
        try:
            await deezerapi.dl_track(metadata.itemid, url, str(download_path))
        except Exception as e:
            LOGGER.error(f"DEEZER: Download failed: {e}")
            await send_text(str(e), task_details)
            return None
        
        await set_metadata(metadata, download_path)
        return download_path


deezer_handler = DeezerHandler()

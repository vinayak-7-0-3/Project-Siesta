import re
import os
import aiohttp
import aiofiles
import aiolimiter

from random import randint
from time import time
from math import ceil
from urllib.parse import urlparse
from Cryptodome.Hash import MD5
from Cryptodome.Cipher import Blowfish, AES
from requests.models import HTTPError

from config import Config
from bot.logger import LOGGER

CHUNK_SIZE = 2048

class APIError(Exception):
    def __init__(self, type, msg, payload):
        self.type = type
        self.msg = msg
        self.payload = payload
    def __str__(self):
        return ', '.join((self.type, self.msg, str(self.payload)))

class DeezerAPI:
    def __init__(self):
        self.gw_light_url = 'https://www.deezer.com/ajax/gw-light.php'
        self.api_token = ''
        self.client_id = '447462'
        self.client_secret = 'a83bf7f38ad2f137e444727cfc3775cf'
        self.ratelimit = aiolimiter.AsyncLimiter(30, 60)

        self.quality = 'MP3_128'

    async def _api_call(self, method, payload={}):
        api_token = self.api_token if method not in ('deezer.getUserData', 'user.getArl') else ''
        params = {
            'method': method,
            'input': 3,
            'api_version': 1.0,
            'api_token': api_token,
            'cid': randint(0, 1_000_000_000),
        }

        async with self.ratelimit:
            async with self.session.post(self.gw_light_url, params=params, json=payload) as r:
                resp = await r.json()

        if resp['error']:
            type = list(resp['error'].keys())[0]
            msg = list(resp['error'].values())[0]
            if type=='VALID_TOKEN_REQUIRED':
                try:
                    await self._api_call('deezer.getUserData')
                    await self._api_call(method, payload)
                    return
                except:
                    pass
            raise APIError(type, msg, resp['payload'])

        if method == 'deezer.getUserData':
            self.api_token = resp['results']['checkForm']
            self.country = resp['results']['COUNTRY']
            self.license_token = resp['results']['USER']['OPTIONS']['license_token']
            self.renew_timestamp = ceil(time())
            self.language = resp['results']['USER']['SETTING']['global']['language']
            
            self.available_formats = ['MP3_128']
            format_dict = {'web_hq': 'MP3_320', 'web_lossless': 'FLAC'}
            for k, v in format_dict.items():
                if resp['results']['USER']['OPTIONS'][k]:
                    self.available_formats.append(v)

        return resp['results']


    async def login(self):
        self.session = aiohttp.ClientSession()
        self.session.headers.update({
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://www.deezer.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'same-origin',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.deezer.com/',
            'accept-language': 'en-US,en;q=0.9',
        })
        #self.legacy_url_cipher = AES.new(Config.DEEZER_TRACK_URL_KEY.encode('ascii'), AES.MODE_ECB)
        self.bf_secret = Config.DEEZER_BF_SECRET.encode('ascii')
        try:
            if Config.DEEZER_ARL:
                await self.login_via_arl(Config.DEEZER_ARL)
            else:
                await self.login_via_email(
                    Config.DEEZER_EMAIL,
                    Config.DEEZER_PASSWORD
                )
        except Exception as e:
            LOGGER.error(f"DEEZER : {e}")
            return False

        return True

    async def login_via_email(self, email, password):
        # server sends set-cookie header with new sid
        async with self.ratelimit:
            await self.session.get('https://www.deezer.com')
        
        password = MD5.new(password.encode()).hexdigest()

        params = {
            'app_id': self.client_id,
            'login': email,
            'password': password,
            'hash': MD5.new((self.client_id + email + password + self.client_secret).encode()).hexdigest(),
        }

        # server sends set-cookie header with account sid
        async with self.ratelimit:
            async with self.session.get('https://connect.deezer.com/oauth/user_auth.php', params=params) as r:
                json = await r.json()

        if 'error' in json:
            raise Exception('Error while getting access token, check your credentials')

        arl = await self._api_call('user.getArl')

        return arl, await self.login_via_arl(arl)

    async def login_via_arl(self, arl):
        cookie = {'arl':arl}
        self.session.cookie_jar.update_cookies(cookie)
        user_data = await self._api_call('deezer.getUserData')
        if not user_data['USER']['USER_ID']:
            raise Exception('Invalid arl')
        self.user = user_data
        return user_data


    async def custom_url_parse(self, link) -> (str, int):
        """
        Args:
            link: Deezer URL
        Returns:
            media type (str), id (int)
        """
        url = urlparse(link)

        if url.hostname == 'link.deezer.com':
            async with self.ratelimit:
                async with self.session.get(link, allow_redirects=True) as r:
                    #resp = await r.json(content_type=None)
                    if r.status != 200:
                        raise Exception(f'DEEZER : Invalid URL: {link}')
                    url = r.real_url

        path_match = re.match(r'^\/(?:[a-z]{2}\/)?(track|album|artist|playlist)\/(\d+)\/?$', url.path)
        if not path_match:
            raise Exception(f'DEEZER : Invalid URL: {link}')

        return path_match.group(1), path_match.group(2)


    async def get_track(self, id):
        res = await self._api_call('deezer.pageTrack', {'sng_id': id})
        return res

    async def get_track_data(self, id):
        res = await self._api_call('song.getData', {'sng_id': id})
        return res

    async def get_track_url(self, id, track_token, track_token_expiry, format):
        # renews license token
        if time() - self.renew_timestamp >= 3600:
            await self._api_call('deezer.getUserData')

        # renews track token
        if time() - track_token_expiry >= 0:
            track_token = await self._api_call('song.getData', {'sng_id': id, 'array_default': ['TRACK_TOKEN']})['TRACK_TOKEN']

        json = {
            'license_token': self.license_token,
            'media': [
                {
                    'type': 'FULL',
                    'formats': [{'cipher': 'BF_CBC_STRIPE', 'format': format}]
                }
            ],
            'track_tokens': [track_token]
        }
        async with self.ratelimit:
            async with self.session.post(
                'https://media.deezer.com/v1/get_url',
                json=json
            ) as r:
                resp = await r.json()

        return resp['data'][0]['media'][0]['sources'][0]['url']


    async def get_album(self, id):
        try:
            res = await self._api_call('deezer.pageAlbum', {'alb_id': id, 'lang': self.language})
        except APIError as e:
            if e.payload:
                res = await self._api_call('deezer.pageAlbum', {'alb_id': e.payload['FALLBACK']['ALB_ID'], 'lang': self.language})
            else:
                raise e
        return res


    async def get_artist_album_ids(self, id, start, nb, credited_albums):
        payload = {
            'art_id': id,
            'start': start,
            'nb': nb,
            'filter_role_id': [0,5] if credited_albums else [0],
            'nb_songs': 0,
            'discography_mode': 'all' if credited_albums else None,
            'array_default': ['ALB_ID']
        }
        resp = await self._api_call('album.getDiscography', payload)
        return [a['ALB_ID'] for a in resp['data']]


    async def get_playlist(self, id, nb, start):
        res = await self._api_call('deezer.pagePlaylist', {'nb': nb, 'start': start, 'playlist_id': id, 'lang': self.language, 'tab': 0, 'tags': True, 'header': True})
        return res


    def _get_blowfish_key(self, track_id):
        md5_id = MD5.new(str(track_id).encode()).hexdigest().encode('ascii')

        key = bytes([md5_id[i] ^ md5_id[i + 16] ^ self.bf_secret[i] for i in range(16)])

        return key
    

    async def dl_track(self, id, url, path):
        bf_key = self._get_blowfish_key(id)
        async with self.session.get(url, allow_redirects=True) as resp:
            buf = bytearray()
            async for data, _ in resp.content.iter_chunks():
                buf += data

            encrypt_chunk_size = 3 * 2048
            os.makedirs(os.path.dirname(path), exist_ok=True)
            async with aiofiles.open(path, "wb") as audio:
                buflen = len(buf)
                for i in range(0, buflen, encrypt_chunk_size):
                    data = buf[i : min(i + encrypt_chunk_size, buflen)]
                    if len(data) >= 2048:
                        decrypted_chunk = (
                            self._decrypt_chunk(bf_key, data[:2048])
                            + data[2048:]
                        )
                    else:
                        decrypted_chunk = data
                    await audio.write(decrypted_chunk)


    @staticmethod
    def _decrypt_chunk(key, data):
        return Blowfish.new(
            key,
            Blowfish.MODE_CBC,
            b"\x00\x01\x02\x03\x04\x05\x06\x07",
        ).decrypt(data)

deezerapi = DeezerAPI()
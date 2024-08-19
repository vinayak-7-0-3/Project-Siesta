import aiohttp
import aiolimiter

from random import randint
from time import time
from math import ceil
from Cryptodome.Hash import MD5
from Cryptodome.Cipher import Blowfish, AES
from requests.models import HTTPError

from config import Config
from bot.logger import LOGGER

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
        self.legacy_url_cipher = AES.new(Config.DEEZER_TRACK_URL_KEY.encode('ascii'), AES.MODE_ECB)
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

deezerapi = DeezerAPI()
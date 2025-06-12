import aiohttp
import asyncio
import aiolimiter

from datetime import datetime, timedelta

from config import Config

from bot.logger import LOGGER

# from orpheusdl-tidal

TIDAL_CLIENT_VERSION = '2.26.1'

class TidalApi:
    def __init__(self):
        self.TIDAL_API_BASE = 'https://api.tidal.com/v1/'
        
        self.ratelimit = aiolimiter.AsyncLimiter(30, 60)

        self.tv_session = None
        self.mobile_hires = None
        self.mobile_atmos = None

        self.quality = 'LOW'
        self.spatial = 'OFF'
        

        self.saved = [] # just for storing opened client session

        self.sub_type = None



    async def _get(self, url, params=None, session=None, refresh=False):
        if params is None:
            params = {}

        # if no session is given, use the first one (default)
        if session is None:
            session = self.saved[0]

        params['countryCode'] = session.country_code
        if 'limit' not in params:
            params['limit'] = '9999'


        async with self.ratelimit:
            async with self.session.get(
                self.TIDAL_API_BASE + url,
                headers=session.auth_headers(),
                params=params
            ) as resp:

                # if the request 401s or 403s, try refreshing the TV/Mobile session in case that helps
                if not refresh and (resp.status == 401 or resp.status == 403):
                    await session.refresh()
                    return await self._get(url, params, session, True)

                resp_json = None
                try:
                    resp_json = await resp.json()
                except:  # some tracks seem to return a JSON with leading whitespace
                    pass
                    """try:
                        #resp_json = json.loads(resp.text.strip())
                        
                    except:  # if this doesn't work, the HTTP status probably isn't 200. Are we rate limited?
                        pass"""

                if not resp_json:
                    raise Exception(f'TIDAL : Response was not valid JSON. HTTP status {resp.status}. {resp.text}')

                if 'status' in resp_json and resp_json['status'] == 404 and \
                        'subStatus' in resp_json and resp_json['subStatus'] == 2001:
                    raise Exception('TIDAL : {}. This might be region-locked.'.format(resp_json['userMessage']))

                if 'status' in resp_json and not resp_json['status'] == 200:
                    raise Exception('TIDAL : ' + str(resp_json))

                return resp_json




    async def get_track(self, track_id):
        return await self._get(f'tracks/{track_id}')


    async def get_album(self, album_id):
        return await self._get('albums/' + str(album_id))
    

    async def get_album_tracks(self, album_id):
        return await self._get('albums/' + str(album_id) + '/tracks')


    async def get_artist(self, artist_id):
        return await self._get('artists/' + str(artist_id))

    async def get_artist_albums(self, artist_id):
        return await self._get('artists/' + str(artist_id) + '/albums')


    async def get_artist_albums_ep_singles(self, artist_id):
        return await self._get('artists/' + str(artist_id) + '/albums', params={'filter': 'EPSANDSINGLES'})


    async def get_stream_url(self, track_id, quality, session):
        return await self._get('tracks/' + str(track_id) + '/playbackinfopostpaywall/v4', {
            'playbackmode': 'STREAM',
            'assetpresentation': 'FULL',
            'audioquality': quality,
            'prefetch': 'false'
        },
        session)



    # call this from bot settings panel only
    async def get_tv_login_url(self):
        """
        Get URL for loggin in using webbrowser
        Returns:
            auth_url: URL for authorization
            error: if any error occured
        """
        self.session = aiohttp.ClientSession()

        if Config.TIDAL_TV_TOKEN is None and Config.TIDAL_TV_SECRET is None:
            return False, "No Token/Secret added"

        self.tv_session = TvSession(
            Config.TIDAL_TV_TOKEN,
            Config.TIDAL_TV_SECRET,
            self.session
        )

        try:
            auth_url = await self.tv_session.get_device()
            return auth_url, None
        except Exception as e:
            return False, e


    async def login_tv(self):
        """
        Needs device code to be fetched before
        Returns:
            sub:(str) subscription type: if login successfull
                (bool) False: if login failed
            err: error if any
        """
        try:
            await self.tv_session.auth()
            self.saved.append(self.tv_session)
            self.sub_type = await self.get_subscription()
            LOGGER.info(f"TIDAL : Loaded account - {self.sub_type}")

            await self.refresh_mobile()

            return self.sub_type, None
        except Exception as e: 
            await self.session.close()
            return False, e


    async def login_from_saved(self, data):
        self.session = aiohttp.ClientSession()

        self.tv_session = TvSession(
            Config.TIDAL_TV_TOKEN,
            Config.TIDAL_TV_SECRET,
            self.session
        )

        self.tv_session.refresh_token = data['refresh_token']
        self.tv_session.country_code = data['country_code']
        self.tv_session.user_id = data['user_id']

        try:
            await self.tv_session.refresh()
            self.saved.append(self.tv_session)
            tv_session = True
        except Exception as e: 
            tv_session = False
            LOGGER.error("TIDAL : Coudn't load TV/Auto - " + str(e))

        # even if tv login failes check for mobile (if set to use mobile)
        await self.refresh_mobile()

        # remove tv session if not authed
        if not tv_session:
            self.tv_session = None

        if self.tv_session.user_id or self.mobile_atmos.user_id or self.mobile_hires.user_id:
            self.sub_type = await self.get_subscription()
        else:
            self.sub_type = 'UNKNOWN'

        return self.sub_type
    

    async def refresh_mobile(self, data=None):
        if Config.TIDAL_MOBILE:
            if Config.TIDAL_MOBILE_TOKEN:
                self.mobile_hires = MobileSession(Config.TIDAL_MOBILE_TOKEN, self.session)
                self.mobile_hires.country_code = self.tv_session.country_code
                self.mobile_hires.refresh_token = self.tv_session.refresh_token
                self.mobile_hires.user_id = self.tv_session.user_id 
                try:
                    await self.mobile_hires.refresh()
                    self.saved.append(self.mobile_hires)
                except Exception as e: 
                    self.mobile_hires = None
                    LOGGER.error("TIDAL : Coudn't load Mobile Hires - " + str(e))

            if Config.TIDAL_ATMOS_MOBILE_TOKEN:
                self.mobile_atmos = MobileSession(Config.TIDAL_ATMOS_MOBILE_TOKEN, self.session)
                self.mobile_atmos.country_code = self.tv_session.country_code
                self.mobile_atmos.refresh_token = self.tv_session.refresh_token
                self.mobile_atmos.user_id = self.tv_session.user_id 
                try:
                    await self.mobile_atmos.refresh()
                    self.saved.append(self.mobile_atmos)
                except Exception as e: 
                    self.mobile_atmos = None
                    LOGGER.error("TIDAL : Coudn't load Mobile Atmos - " + str(e))


    async def get_subscription(self) -> str:
        """
        pick a session and fetch the subscription
        """
        if self.saved != []:
            usersess = self.saved[0]
            async with self.session.get(f'https://api.tidal.com/v1/users/{usersess.user_id}/subscription',
                params={'countryCode': usersess.country_code},
                headers=usersess.auth_headers()
            ) as r:
                json_resp = await r.json()
                if r.status != 200:
                    raise Exception(f"TIDAL : {json_resp['userMessage']}")
                return json_resp['subscription']['type']
        

class MobileSession():
    """
    Args
        token: hires/atmos mobile token (str)
        session: aiohttp session
    """
    def __init__(self, token, session):
        self.session = session

        self.client_id = token
        self.user_id = None
        self.country_code = None
        self.access_token = None
        self.refresh_token = None

        self.TIDAL_AUTH_BASE = 'https://auth.tidal.com/v1/'

    async def refresh(self):
        assert (self.refresh_token is not None)
        assert (self.client_id is not None)

        async with self.session.post(self.TIDAL_AUTH_BASE + 'oauth2/token', data={
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'grant_type': 'refresh_token'
        }) as r:
            json_resp = await r.json()
            if r.status == 200:
                # get user_id in case of direct refresh token login
                if not self.user_id:
                    self.user_id = json_resp['user_id']
                self.access_token = json_resp['access_token']
                self.expires = datetime.now() + timedelta(seconds=json_resp['expires_in'])

                if 'refresh_token' in json_resp:
                    self.refresh_token = json_resp['refresh_token']

            elif r.status == 401:
                raise Exception('TIDAL : ' + json_resp['userMessage'])


    def auth_headers(self):
        return {
            'Host': 'api.tidal.com',
            'X-Tidal-Token': self.client_id,
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'TIDAL_ANDROID/1039 okhttp/3.14.9'
        }


class TvSession():
    """
    Args
        token: tv token (str)
        secret: tv secret (str)
        session: aiohttp session
    """
    def __init__(self, token, secret, session):
        self.TIDAL_AUTH_BASE = 'https://auth.tidal.com/v1/'
        

        self.client_id = token 
        self.client_secret = secret 
        self.access_token = None
        self.refresh_token = None
        self.expires = None
        self.user_id = None
        self.country_code = None
        self.temp_data = None

        # link expiry from tidal
        #self.login_timeout = None
        # url login check
        #self.login_chk_interval = None

        self.session = session

    async def get_device(self):
        async with self.session.post(self.TIDAL_AUTH_BASE + 'oauth2/device_authorization', data={
                'client_id': self.client_id,
                'scope': 'r_usr w_usr'
            }
        ) as r:
            if r.status != 200:
                raise Exception("TIDAL : Invalid TV Client ID or Token")
            else:
                json_resp = await r.json()
                device_code = json_resp['deviceCode']
                user_code = json_resp['userCode']
                #self.login_chk_interval = json_resp['interval']
                #self.login_timeout = json_resp['expiresIn']
                auth_link = f"https://link.tidal.com/{user_code}"

        self.temp_data = {
            'client_id': self.client_id,
            'device_code': device_code,
            'client_secret': self.client_secret,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'scope': 'r_usr w_usr'
        }

        return auth_link

    async def auth(self):
        # keep a timer - not causing infinite wait
        #expiry = datetime.now() + timedelta(seconds=self.login_timeout)
        status_code = 400
        i = 1
        while status_code == 400:
            """if datetime.now() > expiry:
                raise Exception('TIDAL : Authorization Timedout')"""
            r = await self.session.post(self.TIDAL_AUTH_BASE + 'oauth2/token', data=self.temp_data)
            status_code = r.status
            await asyncio.sleep(i)
            i+=1

        json_resp = await r.json()
        r.close()

        if status_code == 200:
            pass
        else:
            raise Exception(f"TIDAL : Auth error - {json_resp['error']}")

        self.access_token = json_resp['access_token']
        self.refresh_token = json_resp['refresh_token']
        self.expires = datetime.now() + timedelta(seconds=json_resp['expires_in'])

        async with self.session.get('https://api.tidal.com/v1/sessions', headers=self.auth_headers()) as r:
            assert (r.status == 200)
            json_resp = await r.json()
            self.user_id = json_resp['userId']
            self.country_code = json_resp['countryCode']

        async with self.session.get(
            f'https://api.tidal.com/v1/users/{self.user_id}?countryCode={self.country_code}',
            headers=self.auth_headers()) as r:
            assert (r.status == 200)


    async def refresh(self):
        # checks before refreshing
        assert (self.refresh_token is not None)
        assert (self.client_id is not None)

        async with self.session.post(self.TIDAL_AUTH_BASE + 'oauth2/token', data={
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }) as r:
            json_resp = await r.json()
            if r.status == 200:
                # get user_id in case of direct refresh token login
                if not self.user_id:
                    self.user_id = json_resp['user_id']
                self.access_token = json_resp['access_token']
                self.expires = datetime.now() + timedelta(seconds=json_resp['expires_in'])

                if 'refresh_token' in json_resp:
                    self.refresh_token = json_resp['refresh_token']

            elif r.status == 401:
                raise Exception('TIDAL : TV/Auto refreshing failed - ' + json_resp['userMessage'])


    def auth_headers(self):
        return {
            'X-Tidal-Token': self.client_id,
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'TIDAL_ANDROID/1039 okhttp/3.14.9'
        }


tidalapi = TidalApi()
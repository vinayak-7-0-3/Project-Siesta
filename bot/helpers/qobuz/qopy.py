# From vitiko98/qobuz-dl
import time
import hashlib
import aiohttp
import aiolimiter

from config import Config

from .bundle import Bundle

from bot.logger import LOGGER

class QoClient:
    def __init__(self):
        self.id = None
        self.secrets = None
        self.session = None
        self.ratelimit = aiolimiter.AsyncLimiter(30, 60)
        self.base = "https://www.qobuz.com/api.json/0.2/"
        self.sec = None
        self.quality = 6
        

    async def api_call(self, epoint, **kwargs):
        if epoint == "user/login":
            if kwargs.get('email'):
                params = {
                    "email": kwargs["email"],
                    "password": kwargs["pwd"],
                    "app_id": self.id,
                }
            else:
                params = {
                    "user_id": kwargs["userid"],
                    "user_auth_token": kwargs["usertoken"],
                    "app_id": self.id,
                }
        elif epoint == "track/get":
            params = {"track_id": kwargs["id"]}
        elif epoint == "album/get":
            params = {"album_id": kwargs["id"]}
        elif epoint == "playlist/get":
            params = {
                "extra": "tracks",
                "playlist_id": kwargs["id"],
                "limit": 500,
                "offset": kwargs["offset"],
            }
        elif epoint == "artist/get":
            params = {
                "app_id": self.id,
                "artist_id": kwargs["id"],
                "limit": 500,
                "offset": kwargs["offset"],
                "extra": "albums",
            }
        elif epoint == "label/get":
            params = {
                "label_id": kwargs["id"],
                "limit": 500,
                "offset": kwargs["offset"],
                "extra": "albums",
            }
        elif epoint == "favorite/getUserFavorites":
            unix = time.time()
            # r_sig = "userLibrarygetAlbumsList" + str(unix) + kwargs["sec"]
            r_sig = "favoritegetUserFavorites" + str(unix) + kwargs["sec"]
            r_sig_hashed = hashlib.md5(r_sig.encode("utf-8")).hexdigest()
            params = {
                "app_id": self.id,
                "user_auth_token": self.uat,
                "type": "albums",
                "request_ts": unix,
                "request_sig": r_sig_hashed,
            }
        elif epoint == "track/getFileUrl":
            unix = time.time()
            track_id = kwargs["id"]
            fmt_id = kwargs["fmt_id"]
            if int(fmt_id) not in (5, 6, 7, 27):
                raise Exception("QOBUZ : Invalid quality id: choose between 5, 6, 7 or 27")
            r_sig = "trackgetFileUrlformat_id{}intentstreamtrack_id{}{}{}".format(
                fmt_id, track_id, unix, kwargs.get("sec", self.sec)
            )
            r_sig_hashed = hashlib.md5(r_sig.encode("utf-8")).hexdigest()
            params = {
                "request_ts": unix,
                "request_sig": r_sig_hashed,
                "track_id": track_id,
                "format_id": fmt_id,
                "intent": "stream",
            }
        else:
            params = kwargs

        return await self.session_call(epoint, params)

    async def session_call(self, epoint, params):
        async with self.ratelimit:
            async with self.session.get(self.base + epoint, params=params) as r:
                if epoint == "user/login":
                    if r.status == 401:
                        raise Exception('QOBUZ : Invalid credentials given..... Disabling QOBUZ')
                    elif r.status == 400:
                        raise Exception("QOBUZ : Invalid App ID. Please Recheck your credentials.... Disabling QOBUZ")
                    else:
                        pass
                elif (
                    epoint in ["track/getFileUrl", "favorite/getUserFavorites"]
                    and r.status == 400
                ):
                    raise Exception("QOBUZ : Invalid App Secret. Please recheck your credentials.... Disabling QOBUZ")
                return await r.json()

    async def auth(self):
        if Config.QOBUZ_EMAIL:
            usr_info = await self.api_call(
                "user/login", 
                email=Config.QOBUZ_EMAIL, 
                pwd=Config.QOBUZ_PASSWORD)
        else:
            usr_info = await self.api_call(
                "user/login", 
                userid=Config.QOBUZ_USER,
                usertoken=Config.QOBUZ_TOKEN)
        if not usr_info:
            return
        if not usr_info["user"]["credential"]["parameters"]:
            raise Exception("QOBUZ : Free accounts are not eligible to download tracks from QOBUZ. Disabling QOBUZ for now")
        self.uat = usr_info["user_auth_token"]
        self.session.headers.update({"X-User-Auth-Token": self.uat})
        self.label = usr_info["user"]["credential"]["parameters"]["short_label"]
        LOGGER.info(f"Loaded QOBUZ - Membership Status: {self.label}")

    async def test_secret(self, sec):
        try:
            await self.api_call("track/getFileUrl", id=5966783, fmt_id=5, sec=sec)
            return True
        except:
            return False

    def get_tokens(self):
        bundle = Bundle()
        self.id = str(bundle.get_app_id())
        self.secrets = [
            secret for secret in bundle.get_secrets().values() if secret
        ]  # avoid empty fields

    async def login(self):
        self.get_tokens()
        self.session = aiohttp.ClientSession()
        #self.rate_limiter = self.get_rate_limiter(30)
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
                "X-App-Id": self.id,
            }
        )
        await self.auth()
        await self.cfg_setup()

    async def cfg_setup(self):
        for secret in self.secrets:
            # Falsy secrets
            if not secret:
                continue
            if await self.test_secret(secret):
                self.sec = secret
                break
        if self.sec is None:
            raise Exception("QOBUZ : Can't find any valid app secret")


qobuz_api = QoClient()
from .utils import *


async def start_qobuz(url:str, user:dict):
    items, item_id, type_dict, content = await check_type(url)
    if items:
        # FOR ARTIST/LABEL
        if type_dict['iterable_key'] == 'albums':
                for item in items:
                    await start_album(item['id'], user)
        else:
        # FOR PLAYLIST 
            for item in items:
                pass
                #await self.startTrack(item['id'], user)
    else:
        if type_dict["album"]:
            await start_album(item_id, user)
        else:
            pass
            #await self.startTrack(item_id, user)


async def start_album(item_id:int, user:dict):
    await get_album_metadata(item_id)




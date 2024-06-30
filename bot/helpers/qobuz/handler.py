from .qopy import qobuz_api


async def start():
    items, item_id, type_dict, content = await check_type(url)
    if items:
        # FOR ARTIST/LABEL
        if type_dict['iterable_key'] == 'albums':
                for item in items:
                    pass
                    #await self.startAlbum(item['id'], user)
        else:
        # FOR PLAYLIST 
            for item in items:
                pass
                #await self.startTrack(item['id'], user)
    else:
        if type_dict["album"]:
            await self.startAlbum(item_id, user)
        else:
            await self.startTrack(item_id, user)




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
        content = [item for item in type_dict["func"](item_id)]
        content_name = content[0]["name"]

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
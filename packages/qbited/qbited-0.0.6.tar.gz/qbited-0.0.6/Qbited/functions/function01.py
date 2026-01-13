import asyncio
from .function05 import Configs
from ..exceptions import Qbitorcancel
from ..exceptions import Qbitskipselection
#==================================================================================

class TEngine:

    async def get01(cli, hid):
        moonus = cli.torrents_info(torrent_hashes=hid)[0]
        return moonus

#==================================================================================

    async def get02(imog, cli, cid, hid):
        while True: #WAIT_FOR_METADATA
            if cid not in Configs.DATA06:
                raise Qbitorcancel(None)
            await asyncio.sleep(1)
            files = cli.torrents_files(torrent_hash=hid)
            if files:
                if len(files) > 1: cli.torrents_pause(torrent_hashes=hid)
                return files

#==================================================================================

    async def get03(cid):
        Configs.DATA07.append(cid)
        while True:
            await asyncio.sleep(1)
            if cid not in Configs.DATA06:
                raise Qbitorcancel(None)
            #if cid not in Configs.DATA07:
                #raise Qbitskipselection(None)
            if cid not in Configs.DATA07:
                break

#==================================================================================

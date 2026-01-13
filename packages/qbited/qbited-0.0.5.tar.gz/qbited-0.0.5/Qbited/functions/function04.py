import os
import shutil
#=====================================================================================================

class Cleand:

    async def get01(dlocation):
        try: shutil.rmtree(dlocation)
        except Exception: pass

    async def get02(imog, thumbnail, flocation):
        try: await imog.delete()
        except Exception: pass
        try: os.remove(flocation)
        except Exception: pass
        try: os.remove(thumbnail)
        except Exception: pass

#=====================================================================================================

    async def get03(cli, hid, dfiles=True):
        try: cli.torrents_delete(torrent_hashes=hid, delete_files=dfiles)
        except Exception: pass

    async def get04(cli, hid, dfiles=False):
        try: cli.torrents_delete(torrent_hashes=hid, delete_files=dfiles)
        except Exception: pass

    async def get05(cli, gid):
        try: dow = cli.get_download(gid)
        except Exception: dow = None
        try: cli.remove(downloads=[dow], force=True, files=True, clean=True) if dow else None
        except Exception: pass

    #=================================================================================================

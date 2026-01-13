from .function05 import Configs

class Cleans:

    async def get01(cid):
        try: Configs.DATA06.remove(cid) if cid in Configs.DATA06 else None
        except Exception: pass

    async def get02(cid):
        try: Configs.DATA07.remove(cid) if cid in Configs.DATA07 else None
        except Exception: pass

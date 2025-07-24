import os

from config import Config, DYNAMIC_VARS

from .tgclient import aio
from .helpers.database.pg_impl import set_db



def load_dynamic_vars():
    for var in DYNAMIC_VARS:
        if not getattr(Config, var):
            setattr(Config, var, set_db.get_variable(var)[0])



if __name__ == "__main__":
    if not os.path.isdir(Config.DOWNLOAD_BASE_DIR):
        os.makedirs(Config.DOWNLOAD_BASE_DIR)
    load_dynamic_vars()
    aio.run()
    
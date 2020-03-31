import re
import sys

from util.logger import Logger
from util.adb import Adb
from util.config import Config
from modules.seal import Seal
from modules.raise_dog import RaiseDog
from util.utils import Utils
from time import sleep



config = Config("config.ini")
Adb.service = config.network["service"]
Adb.device = "-d" if (Adb.service == "PHONE") else "-e"
adb = Adb()
if adb.init():

    Logger.log_msg('Successfully connected to the service.')
    output = Adb.exec_out('wm size').decode('utf-8').strip()
    Logger.log_info(output)

    if not re.search('1080x2340|2340x1080', output):
        Logger.log_error("Resolution is not 2340x1080, please change it.")
        sys.exit()

    # 开启妖气封印
    seal = Seal(config)
    seal.start_logic()

    # 养狗粮
    # raise_dog = RaiseDog(config)
    # raise_dog.start_logic()

else:
    Logger.log_error('Unable to connect to the service.')
    sys.exit()
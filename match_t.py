import re
import sys

from util.logger import Logger
from util.adb import Adb
from util.config import Config
from modules.seal import Seal
from util.utils import Utils, Region, globals_region
from time import sleep

config = Config("config.ini")
Adb.service = config.network["service"]
Adb.device = "-d" if (Adb.service == "PHONE") else "-e"
adb = Adb()
adb.init()


# Utils.update_screen("tmp/2020-03-29 16:47:46.068835.png")
# Utils.find("explore/22", 0.5, True)

def swipeTest():
    Utils.swipe(385, 1037, 1671, 1037, 1000)
    sleep(2)
    Utils.swipe(1689, 878, 1172, 483, 1000)
    sleep(2)
    Utils.swipe(1689, 878, 1828, 483, 1000)


def find_max_levels():
    Utils.update_screen("tmp/2020-03-29 17:29:48.594597.png")
    result = Utils.find_all("combat/level_max", 0.8)
    data = [False, False, False]
    if result and len(result) > 0:
        for (x, y) in result:
            if 500 < x < 764:
                data[0] = True
            elif 764 < x < 1115:
                data[1] = True
            elif 1115 < x < 1550:
                data[2] = True
    print(data)


def replace_dog():
    Logger.log_msg("开始检查是否满级")
    Utils.script_sleep(2)
    Utils.update_screen()
    thug_loc = 1
    all_max = Utils.find_all("combat/level_max", 0.8)
    data = [False, False, False]
    if len(all_max) > 0:
        for (x, y) in all_max:
            if 500 < x < 764:
                data[0] = True
            elif 764 < x < 1115:
                data[1] = True
            elif 1115 < x < 1550:
                data[2] = True

    replace = False
    for i, v in enumerate(data):
        if i != thug_loc and v == True:
            Logger.log_msg("需要替换狗粮")
            replace = True
            break

    if replace:
        # 点击切换狗粮,要选2次
        Logger.log_msg("点击切换狗粮,要选2次")
        Utils.touch_randomly(Region(486, 615, 440, 85))
        Utils.script_sleep(0.1, 0.5)
        Utils.touch_randomly(Region(486, 615, 440, 85))
        Utils.script_sleep()
        # 点击全部
        Logger.log_msg("点击全部")
        Utils.touch_randomly(Region(51, 938, 103, 99))
        Utils.script_sleep()
        # 选中N卡
        Logger.log_msg("选中N卡")
        Utils.touch_randomly(Region(215, 470, 87, 87))
        Utils.script_sleep()
        # 拉动滚动条
        Logger.log_msg("拉动滚动条")
        Utils.swipe(385, 1037, 1671, 1037, 1500)
        Utils.script_sleep(2)

        for i, v in enumerate(data):
            if i != thug_loc and v is True:
                if i == 0:
                    Utils.wait_update_screen()
                    r = Utils.find("combat/level_1", 0.8)
                    Logger.log_msg("替换右边狗粮")
                    Utils.swipe(r.x + 80, r.y + 80, 1800, 523, 1000)
                elif i == 1:
                    Utils.wait_update_screen()
                    r = Utils.find("combat/level_1", 0.8)
                    Logger.log_msg("替换中边狗粮")
                    Utils.swipe(r.x + 80, r.y + 80, 1170, 523, 1000)
                elif i == 2:
                    Utils.wait_update_screen()
                    r = Utils.find("combat/level_1", 0.8)
                    Logger.log_msg("替换左边狗粮")
                    Utils.swipe(r.x + 80, r.y + 80, 500, 523, 1000)
                Utils.script_sleep()
        #
        # Logger.log_msg("点击返回")
        # Utils.touch_randomly(Region(13, 12, 82, 77))
        # Utils.script_sleep(2)
        # Logger.log_msg("战斗")
        # Utils.touch_randomly(globals_region["combat_ready"])
    pass


def find_explore():
    Utils.update_screen()
    Utils.find("home/explore", 0.8, True)


def find_level_1():
    Utils.update_screen("tmp/2020-03-30 13:35:12.661218.png")
    result = Utils.find_all("combat/level_1", 0.8)
    print(result)

    pass


def find1_test():
    # 2020-03-01 09:37:07.134630
    Utils.update_screen("tmp/2020-03-01 09:37:07.134630.png")
    Utils.find_1("duplicate/exp", 0.5, True)
    pass


if __name__ == "__main__":
    find1_test()
    pass

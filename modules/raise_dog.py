import sys
from random import randint
from enum import Enum
from util.utils import Utils, Region, globals_region
from util.logger import Logger


class RaiseDogState(Enum):
    NONE = 0
    EXPLORE = 1
    EXPLORE_PRE = 2
    SCENE = 3
    FIGHT = 4


class RaiseDog(object):
    def __init__(self, config):
        self.enabled = False
        self.config = config
        self.region = {
            "difficult_level": Region(842, 304, 102, 78),
            "start_explore": Region(1532, 768, 190, 83),
        }

    def start_logic(self):
        Logger.log_msg("开始练狗粮")
        self.enabled = True
        loc = RaiseDogState.NONE
        # 打 boss
        find_sec = False
        # 首次进入
        first_time = True
        is_boss = False
        swipe_right = True
        swipe_count = 10

        while True:
            if loc == RaiseDogState.NONE:
                Utils.update_screen()
                if Utils.find_and_touch("home/explore", 0.6):
                    Logger.log_msg("首页，点击探索")
                    Utils.script_sleep()
                    loc = RaiseDogState.EXPLORE
                elif Utils.find("explore/icon_yao"):
                    Logger.log_msg("探索页面")
                    loc = RaiseDogState.EXPLORE
                elif Utils.find("explore/explore_1"):
                    Logger.log_msg("准备进本")
                    Utils.touch_randomly(self.region["difficult_level"])
                    Utils.script_sleep()
                    loc = RaiseDogState.EXPLORE_PRE
                elif Utils.find("duplicate/back"):
                    Logger.log_msg("在副本中")
                    Utils.script_sleep()
                    loc = RaiseDogState.SCENE
                else:
                    Logger.log_msg("未知场景。。")
                continue

            if loc == RaiseDogState.EXPLORE:
                sec = self.config.dog["section"]
                Logger.log_msg(f"查找章节:{sec}")
                # 查找对应章节
                swipe_count = 0
                down = True
                while not find_sec:
                    Utils.update_screen()
                    r = Utils.find(f"explore/{sec}")
                    if swipe_count == 9:
                        swipe_count = 0
                        down = not down
                    if not r:
                        if down:
                            Utils.swipe(2148, 700, 2148, 500, randint(300, 500))
                        else:
                            Utils.swipe(2148, 500, 2148, 700, randint(300, 500))
                        swipe_count += 1
                        Utils.script_sleep(1)
                    else:
                        find_sec = True
                        Utils.touch_randomly(r)
                        loc = RaiseDogState.EXPLORE_PRE
                continue

            if loc == RaiseDogState.EXPLORE_PRE:
                first_time = True
                Logger.log_msg("选中困难")
                Utils.touch_randomly(self.region["difficult_level"])
                Logger.log_msg("点击开始探索")
                Utils.touch_randomly(self.region["start_explore"])
                loc = RaiseDogState.SCENE
                continue

            # 副本中
            if loc == RaiseDogState.SCENE:
                Logger.log_msg("副本中，等待..")
                # 如果已经退出副本了
                if Utils.find("explore/explore_1"):
                    Logger.log_msg("跳出了副本场景，准备进本")
                    first_time = True
                    Utils.touch_randomly(self.region["start_explore"])
                    Utils.script_sleep(2)
                    continue

                if first_time:
                    is_boss = False
                    swipe_right = True
                    swipe_count = 10

                if is_boss:
                    Utils.script_sleep(3)
                    Logger.log_msg("查找胜利品")
                    Utils.update_screen()
                    while Utils.find_and_touch("duplicate/booty"):
                        Logger.log_msg("找到胜利品")
                        Utils.script_sleep(1)
                        Utils.touch_randomly(globals_region["combat_finish"])
                        Utils.script_sleep(1)
                        Utils.update_screen()
                    Logger.log_msg("查找胜利品结束")
                    find_sec = False
                    loc = RaiseDogState.NONE
                    is_boss = False
                    # 等一会跳到探索页面
                    Utils.script_sleep(2)
                    continue

                Utils.update_screen()
                if Utils.find_and_touch("duplicate/boss"):
                    Logger.log_msg("boss出现了..")
                    loc = RaiseDogState.FIGHT
                    Utils.script_sleep(2)
                    is_boss = True
                elif Utils.find_and_touch("duplicate/fire"):
                    loc = RaiseDogState.FIGHT
                    Utils.script_sleep(2)
                    is_boss = False
                else:
                    if swipe_right:
                        Logger.log_msg("划到右边看看")
                        Utils.swipe(1437, 500, 960, 500, randint(300, 500))
                    else:
                        Logger.log_msg("划到左边看看")
                        Utils.swipe(960, 500, 1437, 500, randint(300, 500))

                    swipe_count -= 1
                    if swipe_count < (swipe_count >> 1):
                        Logger.log_msg("换个方向")
                        swipe_right = not swipe_right

                if swipe_count < 0:
                    Logger.log_msg("超过最大次数重新判断当前页面。")
                    loc = RaiseDogState.NONE
                continue

            if loc == RaiseDogState.FIGHT:
                Utils.update_screen()
                if Utils.find("duplicate/back"):
                    Logger.log_msg("副本中")
                    loc = RaiseDogState.SCENE
                    is_boss = False
                    continue

                if first_time:
                    Logger.log_msg("开始检查是否满级")
                    Utils.script_sleep()
                    Utils.update_screen()
                    thug_loc = int(self.config.dog["thug_loc"])
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
                        Utils.touch_randomly(Region(495, 586, 192, 247))
                        Utils.script_sleep(0.1, 0.5)
                        Utils.touch_randomly(Region(495, 586, 192, 247))
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
                        Utils.swipe(385, 1037, 1671, 1037, randint(1500, 2000))
                        Utils.script_sleep(2)

                        for i, v in enumerate(data):
                            if i != thug_loc and v is True:
                                if i == 0:
                                    Utils.wait_update_screen()
                                    r = Utils.find("combat/level_1", 0.8)
                                    Logger.log_msg("替换右边狗粮")
                                    Utils.swipe(r.x + 80, r.y + 80, 1800, 523, randint(300, 500))
                                elif i == 1:
                                    Utils.wait_update_screen()
                                    r = Utils.find("combat/level_1", 0.8)
                                    Logger.log_msg("替换中边狗粮")
                                    Utils.swipe(r.x + 80, r.y + 80, 1170, 523, randint(300, 500))
                                elif i == 2:
                                    Utils.wait_update_screen()
                                    r = Utils.find("combat/level_1", 0.8)
                                    Logger.log_msg("替换左边狗粮")
                                    Utils.swipe(r.x + 80, r.y + 80, 500, 523, randint(300, 500))
                                Utils.script_sleep()

                        Logger.log_msg("战斗")
                        Utils.touch_randomly(globals_region["combat_ready"])

                if Utils.find("combat/ready"):
                    first_time = False
                    Logger.log_msg("战斗")
                    Utils.touch_randomly(globals_region["combat_ready"])
                    continue

                if Utils.find("combat/manual"):
                    first_time = False
                    Logger.log_msg("开启自动")
                    Utils.touch_randomly(globals_region["combat_manual"])
                    continue

                if Utils.find("combat/victory"):
                    Logger.log_msg("胜利")
                    Utils.touch_randomly(globals_region["combat_finish"])
                    continue

                if Utils.find("combat/booty"):
                    Logger.log_msg("获取胜利品。。")
                    Utils.touch_randomly(globals_region["combat_finish"])
                    # 结束战斗后，留多点时间
                    Utils.script_sleep(3, 1)
                    loc = RaiseDogState.SCENE
                    continue

                if Utils.find("combat/fail"):
                    Logger.log_msg("挑战失败。。")
                    is_boss = False
                    Utils.touch_randomly(globals_region["combat_finish"])
                    # 结束战斗后，留多点时间
                    Utils.script_sleep(3, 1)
                    loc = RaiseDogState.SCENE
                    continue

            Utils.script_sleep(1, 1)

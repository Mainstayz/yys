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
        self.find_sec = False
        self.first_time = True
        self.is_boss = False
        self.swipe_right = True
        self.swipe_count = 0
        self.retry_count = 0

    def reset(self):
        self.find_sec = False
        self.first_time = True
        self.is_boss = False
        self.swipe_right = True
        self.swipe_count = 0
        self.retry_count = 0

    def start_logic(self):
        Logger.log_msg("开始练狗粮")
        self.enabled = True
        loc = RaiseDogState.NONE
        while True:
            if loc == RaiseDogState.NONE:
                Utils.update_screen()
                if Utils.find_and_touch("home/explore", 0.6, True):
                    Logger.log_msg("首页，点击探索")
                    Utils.script_sleep(3)
                    loc = RaiseDogState.EXPLORE
                    self.reset()
                elif Utils.find("explore/icon_yao"):
                    Logger.log_msg("探索页面")
                    loc = RaiseDogState.EXPLORE
                    self.reset()
                    if Utils.find_and_touch("explore/booty"):
                        Logger.log_msg("！！发现宝箱 ！！")
                        Utils.script_sleep(2)
                        Utils.touch_randomly()
                        Utils.script_sleep(1)

                elif Utils.find("explore/explore_1"):
                    Logger.log_msg("准备进本")
                    Utils.touch_randomly(self.region["difficult_level"])
                    Utils.script_sleep()
                    loc = RaiseDogState.EXPLORE_PRE
                    self.first_time = True
                    self.is_boss = False
                    self.swipe_right = True
                    self.swipe_count = 0
                    self.retry_count = 0
                elif Utils.find("duplicate/back"):
                    Logger.log_msg("在副本中")
                    Utils.script_sleep()
                    loc = RaiseDogState.SCENE
                elif Utils.find("combat/ready"):
                    self.first_time = False
                    Logger.log_msg("战斗")
                    Utils.touch_randomly(globals_region["combat_ready"])
                    loc = RaiseDogState.FIGHT
                else:
                    Logger.log_msg("未知场景。。")
                    self.retry_count -= 1
                    if self.retry_count <= 0:
                        sys.exit(-1)
                continue

            if loc == RaiseDogState.EXPLORE:
                sec = self.config.dog["section"]
                Logger.log_msg(f"查找章节:{sec}")
                # 查找对应章节
                find_count = 0
                down = True
                while not self.find_sec:
                    # 尝试的次数
                    if find_count > 20:
                        print("无法找到对应的章节")
                        sys.exit(-1)

                    if find_count == 10:
                        find_count = 0
                        down = bool(1 - down)

                    Utils.update_screen()

                    r = Utils.find(f"explore/{sec}")
                    if not r:
                        if down:
                            Utils.swipe(2148, 700, 2148, 500, randint(300, 500))
                        else:
                            Utils.swipe(2148, 500, 2148, 700, randint(300, 500))
                        find_count += 1
                        Utils.script_sleep(1)
                    else:
                        self.find_sec = True
                        Utils.touch_randomly(r)
                        loc = RaiseDogState.EXPLORE_PRE
                continue

            if loc == RaiseDogState.EXPLORE_PRE:
                # reset
                self.reset()
                Logger.log_msg("选中困难")
                Utils.touch_randomly(self.region["difficult_level"])
                Logger.log_msg("点击开始探索")
                Utils.touch_randomly(self.region["start_explore"])
                loc = RaiseDogState.SCENE
                continue

            # 副本中
            if loc == RaiseDogState.SCENE:
                Logger.log_msg("副本场景")
                if self.is_boss:
                    Utils.script_sleep(3)
                    Logger.log_msg("打完boss, 副本结束")
                    Utils.update_screen()
                    while Utils.find_and_touch("duplicate/booty"):
                        Logger.log_msg("找到胜利品")
                        Utils.script_sleep(1)
                        Utils.touch_randomly(globals_region["combat_finish"])
                        Utils.script_sleep(1)
                        Utils.update_screen()
                    Logger.log_msg("查找胜利品结束")
                    loc = RaiseDogState.NONE
                    # 等一会跳到探索页面
                    Utils.script_sleep(2)
                    continue

                Utils.update_screen()
                if Utils.find_and_touch("duplicate/boss"):
                    Logger.log_msg("boss出现了..")
                    loc = RaiseDogState.FIGHT
                    Utils.script_sleep(2)
                    self.is_boss = True
                elif Utils.find_and_touch("duplicate/fire"):
                    loc = RaiseDogState.FIGHT
                    Utils.script_sleep(2)
                    self.is_boss = False
                else:
                    if self.swipe_right:
                        Logger.log_msg("划到右边看看")
                        Utils.swipe(1437, 500, 960, 500, randint(300, 500))
                    else:
                        Logger.log_msg("划到左边看看")
                        Utils.swipe(960, 500, 1437, 500, randint(300, 500))
                    #
                    Utils.script_sleep(1)

                    self.swipe_count += 1
                    if self.swipe_count % 6 == 0:
                        Logger.log_msg("换个方向")
                        self.swipe_right = bool(1 - self.swipe_right)

                if self.swipe_count > 20:
                    Logger.log_msg("超过最大次数重新判断当前页面。")
                    loc = RaiseDogState.NONE
                continue

            if loc == RaiseDogState.FIGHT:

                # 由于怪物是跑动的，解决有时点击不中的bug
                Utils.update_screen()
                if Utils.find("duplicate/back"):
                    Logger.log_msg("点不着，重试..")
                    loc = RaiseDogState.SCENE
                    self.is_boss = False
                    continue

                if self.first_time:
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
                    self.first_time = False
                    continue

                if Utils.find("combat/ready"):
                    self.first_time = False
                    Logger.log_msg("战斗")
                    Utils.touch_randomly(globals_region["combat_ready"])
                    continue

                if Utils.find("combat/manual"):
                    self.first_time = False
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
                    self.is_boss = False
                    Utils.touch_randomly(globals_region["combat_finish"])
                    # 结束战斗后，留多点时间
                    Utils.script_sleep(3, 1)
                    loc = RaiseDogState.SCENE
                    continue

            Utils.script_sleep(2, 1)

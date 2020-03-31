import sys
from random import randint

from util.utils import Utils, Region
from util.logger import Logger


class Seal(object):
    def __init__(self, config):
        self.enabled = False
        self.config = config
        self.region = {
            "home_team_up": Region(663, 907, 89, 108),
            "assist_challenge": Region(2170, 896, 163, 174),
            "combat_ready": Region(2064, 726, 221, 210),
            "combat_manual": Region(40, 949, 100, 92),
            "combat_finish": Region(1674, 612, 555, 419),
            "combat_cancel_invite": Region(864, 608, 258, 86),
            "auto_team_up": Region(1264, 898, 256, 84),
        }

    def start_logic(self):
        Logger.log_msg("开始妖气封印")
        self.enabled = True
        is_find_yqfy = False
        while True:
            # 更新屏幕
            Utils.update_screen()

            if Utils.find("home/menu_close", 0.8):
                Logger.log_msg("卷轴被关闭，展开")
                Utils.touch_center(Region(2145, 872, 149, 168))

            # 解决封印协同任务
            if Utils.find("popup/close", 0.8):
                Logger.log_msg("封印任务弹窗")
                Utils.touch_center(Region(1461, 740, 228, 77))

            if Utils.find("home/team_up", 0.96):

                hp = Utils.read_numbers(1727, 31, 86, 35)
                Logger.log_msg(f"首页,当前体力：{hp}")

                # hp_limit = self.config.seal["hp_limit"]
                # if hp <= int(hp_limit):
                #     Logger.log_warning("体力过少，退出")
                #     sys.exit()

                if Utils.find("home/seal_queuing", 0.9):
                    Logger.log_msg("正在排队")
                    Utils.script_sleep(13, 2)
                    continue

                if Utils.find("home/team_up"):
                    Utils.touch_center(self.region["home_team_up"])
                    continue

            if Utils.find("teamup/back"):
                Logger.log_msg("进入组队页面")

                name = self.config.seal["monster"]
                t = Utils.find("seal/" + name + "_normal")
                t1 = Utils.find("seal/" + name + "_select")
                if t and t1:
                    Logger.log_msg(f"找到{name}")

                    if t.vol > t1.vol:
                        Logger.log_msg(f"点击{name}")
                        Utils.touch_randomly(t)

                    Utils.script_sleep()
                    Logger.log_msg(f"点击自动匹配")
                    Utils.touch_randomly(self.region["auto_team_up"])
                    continue

                if is_find_yqfy:
                    Logger.log_msg(f"滑一滑，找找{name}")
                    Utils.swipe(950, 800, 950, 400, randint(80, 120))
                    Utils.script_sleep(1, 2)
                    continue

                seal = Utils.find("seal/yqfy_normal", 0.95, False)
                if seal:
                    Logger.log_msg("找到妖气封印")
                    is_find_yqfy = True
                    Utils.touch_randomly(seal)
                    continue
                else:
                    Logger.log_msg("找不到妖气封印...滑一下")
                    Utils.swipe(600, 800, 600, 400, randint(100, 150))
                    Utils.script_sleep(1, 2)
                    continue

            if Utils.find("team/back"):
                Logger.log_msg("进入组队页面")
                r = Utils.find("team/challenge")
                if r:
                    Logger.log_msg("成为队长了，挑战～")
                    Utils.touch_randomly(self.region["assist_challenge"])
                continue

            if Utils.find("combat/ready"):
                Logger.log_msg("战斗")
                Utils.touch_randomly(self.region["combat_ready"])
                continue

            if Utils.find("combat/manual"):
                Logger.log_msg("开启自动")
                Utils.touch_randomly(self.region["combat_manual"])
                continue

            if Utils.find("combat/victory"):
                Logger.log_msg("胜利")
                Utils.touch_randomly(self.region["combat_finish"])
                Utils.script_sleep(1, 1)
                continue

            if Utils.find("combat/booty"):
                Logger.log_msg("获取胜利品。。")
                Utils.touch_randomly(self.region["combat_finish"])
                continue

            if Utils.find("combat/fail"):
                Logger.log_msg("挑战失败。。")
                Utils.touch_randomly(self.region["combat_finish"])
                continue

            if Utils.find("combat/auto_invite"):
                Logger.log_msg("取消自动邀请队友")
                Utils.touch_randomly(self.region["combat_cancel_invite"])
                continue

            Utils.script_sleep(2, 1)

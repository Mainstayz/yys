import cv2
import numpy
import time
from imutils import contours, grab_contours
from multiprocessing.pool import ThreadPool
from datetime import datetime, timedelta
from random import uniform, gauss, randint
from scipy import spatial
from util.adb import Adb
from util.logger import Logger
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


class Region(object):
    x, y, w, h, vol = 0, 0, 0, 0, 0

    def __init__(self, x, y, w, h, v=0):
        """Initializes a region.

        Args:
            x (int): Initial x coordinate of the region (top-left).
            y (int): Initial y coordinate of the region (top-left).
            w (int): Width of the region.
            h (int): Height of the region.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vol = v

    def equal_approximated(self, region, tolerance=15):
        """Compares this region to the one received and establishes if they are the same
        region tolerating a difference in pixels up to the one prescribed by tolerance.

        Args:
            region (Region): The region to compare to.
            tolerance (int, optional): Defaults to 15.
                Highest difference of pixels tolerated to consider the two Regions equal.
                If set to 0, the method becomes a "strict" equal.
        """
        valid_x = (self.x - tolerance, self.x + tolerance)
        valid_y = (self.y - tolerance, self.y + tolerance)
        valid_w = (self.w - tolerance, self.w + tolerance)
        valid_h = (self.h - tolerance, self.h + tolerance)
        return (
                valid_x[0] <= region.x <= valid_x[1]
                and valid_y[0] <= region.y <= valid_y[1]
                and valid_w[0] <= region.w <= valid_w[1]
                and valid_h[0] <= region.h <= valid_h[1]
        )


screen = None
last_ocr = ""


class Utils(object):
    small_boss_icon = False
    DEFAULT_SIMILARITY = 0.9
    locations = ()

    @staticmethod
    def multithreader(threads):
        """Method for starting and threading multithreadable Threads in
        threads.

        Args:
            threads (list): List of Threads to multithread.
        """
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    @staticmethod
    def script_sleep(base=0.5, flex=1):
        """Method for putting the program to sleep for a random amount of time.
        If base is not provided, defaults to somewhere along with 0.3 and 0.7
        seconds. If base is provided, the sleep length will be between base
        and 2*base. If base and flex are provided, the sleep length will be
        between base and base+flex. The global SLEEP_MODIFIER is than added to
        this for the final sleep length.

        Args:
            base (int, optional): Minimum amount of time to go to sleep for.
            flex (int, optional): The delta for the max amount of time to go
                to sleep for.
        """
        time.sleep(uniform(base, base + flex))

    @staticmethod
    def update_screen(file=None):
        """Uses ADB to pull a screenshot of the device and then read it via CV2
        and then returns the read image. The image is in a grayscale format.

        Returns:
            image: A CV2 image object containing the current device screen.
        """
        global screen
        screen = None

        if file:
            screen = cv2.imread(file, 0)
            return screen

        while screen is None:
            if Adb.legacy:
                screen = cv2.imdecode(
                    numpy.fromstring(Adb.exec_out(r"screencap -p | sed s/\r\n/\n/"), dtype=numpy.uint8), 0
                )
            else:
                screen = cv2.imdecode(numpy.fromstring(Adb.exec_out("screencap -p"), dtype=numpy.uint8), 0)
            return screen

    @staticmethod
    def save_screen():
        scr = Utils.get_color_screen()
        cv2.imwrite(f"tmp/{datetime.now()}.png", scr)

    @classmethod
    def wait_update_screen(cls, time=None):
        """Delayed update screen.

        Args:
            time (int, optional): seconds of delay.
        """
        if time is None:
            cls.script_sleep()
        else:
            cls.script_sleep(time)
        cls.update_screen()

    @staticmethod
    def get_color_screen():
        """Uses ADB to pull a screenshot of the device and then read it via CV2
        and then returns the read image. The image is in a BGR format.

        Returns:
            image: A CV2 image object containing the current device screen.
        """
        color_screen = None
        while color_screen is None:
            if Adb.legacy:
                color_screen = cv2.imdecode(
                    numpy.fromstring(Adb.exec_out(r"screencap -p | sed s/\r\n/\n/"), dtype=numpy.uint8), 1
                )
            else:
                color_screen = cv2.imdecode(numpy.fromstring(Adb.exec_out("screencap -p"), dtype=numpy.uint8), 1)
        return color_screen

    @staticmethod
    def read_numbers(x, y, w, h, max_digits=5):
        """ Method to ocr numbers.
            Returns int.
        """
        text = []

        crop = screen[y: y + h, x: x + w]
        crop = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        # # 使用阈值进行二值化
        thresh = cv2.threshold(crop, 0, 255, cv2.THRESH_OTSU)[1]
        # cv2.imwrite('thresh1.png', thresh)

        #  在阈值图像中查找轮廓
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnts = grab_contours(cnts)
        cnts = contours.sort_contours(cnts, method="left-to-right")[0]
        numpy.argmax
        if len(cnts) > max_digits:
            return 0

        # 循环处理每一个数字
        for c in cnts:
            scores = []

            # 计算轮廓的边界框
            (x, y, w, h) = cv2.boundingRect(c)

            # 画圈，debug 用
            # cv2.rectangle(thresh, (x, y), (x + w, y + h), (255, 255, 255), 2)
            # cv2.imshow("crop", thresh)
            # cv2.waitKey()

            # 获取ROI区域
            roi = thresh[y: y + h, x: x + w]
            # cv2.imwrite(f"{v}.png", roi)
            # cv2.imshow("crop", roi)
            # cv2.waitKey()

            # 分别计算每一段的宽度和高度
            row, col = roi.shape[:2]

            width = round(abs((50 - col)) / 2) + 5
            height = round(abs((94 - row)) / 2) + 5

            # 边界扩展
            resized = cv2.copyMakeBorder(
                roi, top=height, bottom=height, left=width, right=width, borderType=cv2.BORDER_CONSTANT, value=[0, 0, 0]
            )

            # cv2.imshow("resized", resized)
            # cv2.waitKey()

            for x in range(0, 10):
                template = cv2.imread("assets/number/{}.png".format(x), 0)
                result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
                (_, score, _, _) = cv2.minMaxLoc(result)
                scores.append(score)

            # 获取最大值下标
            text.append(str(numpy.argmax(scores)))

        text = "".join(text)
        return int(text)

    @classmethod
    def check_oil(cls, limit=0):
        global last_ocr
        oil = []

        if limit == 0:
            return True

        cls.menu_navigate("menu/button_battle")

        while len(oil) < 5:
            _res = int(cls.read_numbers(970, 38, 101, 36))
            if last_ocr == "" or abs(_res - last_ocr) < 600:
                oil.append(_res)

        last_ocr = max(set(oil), key=oil.count)
        Logger.log_debug("Current oil: " + str(last_ocr))

        if limit > last_ocr:
            Logger.log_error("Oil below limit: " + str(last_ocr))
            return False

        return last_ocr

    @classmethod
    def find(cls, image, similarity=DEFAULT_SIMILARITY, show=False):
        """Finds the specified image on the screen

        Args:
            image (string): [description]
            similarity (float, optional): Defaults to DEFAULT_SIMILARITY.
                Percentage in similarity that the image should at least match.

        Returns:
            Region: region object containing the location and size of the image
        """
        template = cv2.imread("assets/{}.png".format(image), 0)

        width, height = template.shape[::-1]
        match = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        value, location = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]

        if show:
            cv2.rectangle(screen, location, (location[0] + width, location[1] + height), (0, 0, 225), 2)
            cv2.namedWindow("MatchResult", 0)
            cv2.resizeWindow("MatchResult", 640, 480)
            cv2.imshow("MatchResult", screen)
            cv2.waitKey()
            cv2.destroyAllWindows()

        if value >= similarity:
            return Region(location[0], location[1], width, height, value)
        return None

    @classmethod
    def find_1(cls, image, similarity=DEFAULT_SIMILARITY, show=False):
        template = cv2.imread("assets/{}.png".format(image), 0)

        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(template, None)
        kp2, des2 = orb.detectAndCompute(screen, None)

        # plt.imshow(template), plt.show()
        # plt.imshow(screen), plt.show()

        # 定义FLANN匹配器
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        # 使用KNN算法匹配
        des1 = des1.astype('float32')
        des2 = des2.astype('float32')
        matches = flann.knnMatch(des1, des2, k=2)

        # 去除错误匹配
        good = []
        for m, n in matches:
            # if m.distance < 0.1 * n.distance:
            good.append(m)

        # if len(good) > 10:
        #     # 改变数组的表现形式，不改变数据内容，数据内容是每个关键点的坐标位置
        #     src_pts = numpy.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        #     dst_pts = numpy.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        #     # findHomography 函数是计算变换矩阵
        #     # 参数cv2.RANSAC是使用RANSAC算法寻找一个最佳单应性矩阵H，即返回值M
        #     # 返回值：M 为变换矩阵，mask是掩模
        #     M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        #     # ravel方法将数据降维处理，最后并转换成列表格式
        #     matchesMask = mask.ravel().tolist()
        #     # 获取img1的图像尺寸
        #     h, w = template.shape
        #     # pts是图像img1的四个顶点
        #     pts = numpy.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        #     # 计算变换后的四个顶点坐标位置
        #     dst = cv2.perspectiveTransform(pts, M)
        #
        #     # b = np.int32(dst).reshape(4, 2)
        #     # img_temp = img2.copy()
        #     # cv2.fillConvexPoly(img_temp, b, 0)
        #
        #     # 根据四个顶点坐标位置在img2图像画出变换后的边框
        #     img2 = cv2.polylines(screen, [numpy.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA)
        # else:
        #     print("Not enough matches are found - %d/%d") % (len(good), MIN_MATCH_COUNT)
        matchesMask = None
        #

        draw_params = dict(
            matchColor=(0, 255, 0),  # draw matches in green color
            singlePointColor=None,
            matchesMask=matchesMask,  # draw only inliers
            flags=2,
        )

        img3 = cv2.drawMatches(template, kp1, screen, kp2, good, None, **draw_params)
        plt.imshow(img3, "gray"), plt.show()

        pass

    @classmethod
    def find_all(cls, image, similarity=DEFAULT_SIMILARITY, useMask=False) -> object:
        """Finds all locations of the image on the screen

        Args:
            image (string): Name of the image.
            similarity (float, optional): Defaults to DEFAULT_SIMILARITY.
                Percentage in similarity that the image should at least match.
            useMask (boolean, optional): Defaults to False.
                If set to True, this function uses a different comparison method and
                a mask when searching for match.

        Returns:
            array: Array of all coordinates where the image appears
        """
        del cls.locations

        if useMask:
            comparison_method = cv2.TM_CCORR_NORMED
            mask = cv2.imread("assets/{}_mask.png".format(image), 0)
        else:
            comparison_method = cv2.TM_CCOEFF_NORMED
            mask = None

        template = cv2.imread("assets/{}.png".format(image), 0)
        match = cv2.matchTemplate(screen, template, comparison_method, mask=mask)
        cls.locations = numpy.where(match >= similarity)

        pool = ThreadPool(processes=4)
        count = 1.20
        results_list = []

        while (len(cls.locations[0]) < 1) and (count > 0.80):
            result = pool.apply_async(cls.match_resize, (template, count, comparison_method, similarity, useMask, mask))
            count -= 0.02
            results_list.append(result)
            result = pool.apply_async(cls.match_resize, (template, count, comparison_method, similarity, useMask, mask))
            cls.script_sleep(0.01)
            count -= 0.02
            results_list.append(result)

        pool.close()
        pool.join()

        # extracting locations from pool's results
        for i in range(0, len(results_list)):
            cls.locations = numpy.append(cls.locations, results_list[i].get(), axis=1)

        return cls.filter_similar_coords(list(zip(cls.locations[1], cls.locations[0])))

    @classmethod
    def match_resize(cls, image, scale, comparison_method, similarity=DEFAULT_SIMILARITY, useMask=False, mask=None):
        template_resize = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
        if useMask:
            mask_resize = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
        else:
            mask_resize = None
        match_resize = cv2.matchTemplate(screen, template_resize, comparison_method, mask=mask_resize)
        return numpy.where(match_resize >= similarity)

    @classmethod
    def resize_and_match(
            cls, templateImage, scale, similarity=DEFAULT_SIMILARITY, interpolationMethod=cv2.INTER_NEAREST
    ):
        template_resize = cv2.resize(templateImage, None, fx=scale, fy=scale, interpolation=interpolationMethod)
        width, height = template_resize.shape[::-1]
        match = cv2.matchTemplate(screen, template_resize, cv2.TM_CCOEFF_NORMED)
        value, location = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]
        if value >= similarity:
            return Region(location[0], location[1], width, height, value)

    @classmethod
    def touch(cls, coords):
        """Sends an input command to touch the device screen at the specified
        coordinates via ADB

        Args:
            coords (array): An array containing the x and y coordinate of
                where to touch the screen
        """
        Adb.shell("input swipe {} {} {} {} {}".format(coords[0], coords[1], coords[0], coords[1], randint(50, 120)))
        cls.script_sleep()

    @classmethod
    def touch_randomly(cls, region=Region(0, 0, 2340, 1080)):
        """Touches a random coordinate in the specified region

        Args:
            region (Region, optional): Defaults to Region(0, 0, 1280, 720).
                specified region in which to randomly touch the screen
        """
        x = cls.random_coord(region.x, region.x + region.w)
        y = cls.random_coord(region.y, region.y + region.h)
        cls.touch([x, y])

    @classmethod
    def touch_center(cls, region=Region(0, 0, 2340, 1080)):
        """Touches a random coordinate in the specified region

        Args:
            region (Region, optional): Defaults to Region(0, 0, 1280, 720).
                specified region in which to randomly touch the screen
        """
        x = region.x + (region.w >> 1)
        y = region.y + (region.h >> 1)
        cls.touch([x, y])

    @classmethod
    def swipe(cls, x1, y1, x2, y2, ms, update_screen=False):
        """Sends an input command to swipe the device screen between the
        specified coordinates via ADB

        Args:
            x1 (int): x-coordinate to begin the swipe at.
            y1 (int): y-coordinate to begin the swipe at.
            x2 (int): x-coordinate to end the swipe at.
            y2 (int): y-coordinate to end the swipe at.
            ms (int): Duration in ms of swipe. This value shouldn't be lower than 300, better if it is higher.
        """
        Adb.shell("input swipe {} {} {} {} {}".format(x1, y1, x2, y2, ms))
        if update_screen:
            cls.update_screen()

    @classmethod
    def find_and_touch(cls, image, similarity=DEFAULT_SIMILARITY):
        """Finds the image on the screen and touches it if it exists

        Args:
            image (string): Name of the image.
            similarity (float, optional): Defaults to DEFAULT_SIMILARITY.
                Percentage in similarity that the image should at least match.

        Returns:
            bool: True if the image was found and touched, false otherwise
        """
        region = cls.find(image, similarity)
        if region is not None:
            cls.touch_randomly(region)
            return True
        return False

    @classmethod
    def random_coord(cls, min_val, max_val):
        """Wrapper method that calls cls._randint() or cls._random_coord() to
        generate the random coordinate between min_val and max_val, depending
        on which return line is enabled.

        Args:
            min_val (int): Minimum value of the random number.
            max_val (int): Maximum value of the random number.

        Returns:
            int: The generated random number
        """
        return cls._randint(min_val, max_val)
        # return cls._randint_gauss(min_val, max_val)

    @staticmethod
    def _randint(min_val, max_val):
        """Method to generate a random value based on the min_val and max_val
        with a uniform distribution.

        Args:
            min_val (int): Minimum value of the random number.
            max_val (int): Maximum value of the random number.

        Returns:
            int: The generated random number
        """
        return randint(min_val, max_val)

    @classmethod
    def filter_similar_coords(cls, coords):
        """Filters out coordinates that are close to each other.

        Args:
            coords (array): An array containing the coordinates to be filtered.

        Returns:
            array: An array containing the filtered coordinates.
        """
        Logger.log_debug("Coords: " + str(coords))
        filtered_coords = []
        if len(coords) > 0:
            filtered_coords.append(coords[0])
            for coord in coords:
                if cls.find_closest(filtered_coords, coord)[0] > 50:
                    filtered_coords.append(coord)
        Logger.log_debug("Filtered Coords: " + str(filtered_coords))
        return filtered_coords

    @staticmethod
    def find_closest(coords, coord):
        """Utilizes a k-d tree to find the closest coordiante to the specified
        list of coordinates.

        Args:
            coords (array): Array of coordinates to search.
            coord (array): Array containing x and y of the coordinate.

        Returns:
            array: An array containing the distance of the closest coordinate
            in the list of coordinates to the specified coordinate as well the
            index of where it is in the list of coordinates
        """
        return spatial.KDTree(coords).query(coord)


globals_region = {
    "home_team_up": Region(663, 907, 89, 108),
    "assist_challenge": Region(2170, 896, 163, 174),
    "combat_ready": Region(2064, 726, 221, 210),
    "combat_manual": Region(40, 949, 100, 92),
    "combat_finish": Region(1674, 612, 555, 419),
    "combat_cancel_invite": Region(864, 608, 258, 86),
    "auto_team_up": Region(1264, 898, 256, 84),
}

#!/usr/bin/python3
# -*- coding:utf-8 -*-

"""
author：yannan1, liying50
since：2023-11-29
"""
import cv2 as cv
import numpy as np
import re
from typing import List, Tuple
from collections import namedtuple
from visioncube import rgb_to_gray
from visioncube.recognition import PPOCR

from ..common import AbstractTransform, eval_arg

__all__ = ["ThresholdingImage", "InRangeThreshold", "BarCodeMask", "DateCodeMask", "ColorLineDefectDetect"]


class ThresholdingImage(AbstractTransform):

    def __init__(
        self,
        threshold1: float = 0.0,
        threshold2: float = 255.0,
        method: str = "auto",
        kernel_size: int = 3,
        offset: int = 0,
        kernel_mode="mean",
    ):
        """ThresholdingImage, 图像二值化, 颜色变换

        Args:
            threshold1: Threshold1, 图像阈值1, [0.0, 255.0, 0.1], 0.0
            threshold2: Threshold2, 图像阈值2, [0.0, 255.0, 0.1], 255.0
            method: Method, 计算阈值的方法, ['auto', 'single_thr', 'triangle', 'adaptive', 'double_thr'], "auto"
            kernel_size: Kernel size, 核数, (0, 500), 3
            offset: Offset, 偏移, [0, 255, 1], 0
            kernel_mode: Kernel mode, 核类型, ['mean', 'gaussian'], 'mean'
        """
        super().__init__(use_gpu=False)
        self.thr1 = threshold1
        self.thr2 = threshold2

        if method not in ["auto", "single_thr", "triangle", "adaptive", "double_thr"]:
            raise ValueError("Method Error!")
        if kernel_mode.lower() not in ["mean", "gaussian"]:
            raise ValueError("Kernel mode error!")

        self.method = method
        self.kernel_size = kernel_size
        self.offset = offset

        if kernel_mode.lower() == "mean":
            self.kernel_mode = cv.ADAPTIVE_THRESH_MEAN_C
        elif kernel_mode.lower() == "gaussian":
            self.kernel_mode = cv.ADAPTIVE_THRESH_GAUSSIAN_C

    def _apply(self, sample):

        if sample.image is None:
            return sample

        gray = rgb_to_gray(sample.image)
        mask = np.zeros(gray.shape, dtype=np.uint8)

        if self.method == "auto":
            ret, mask = cv.threshold(gray, 0, 255, cv.THRESH_OTSU)
        elif self.method == "single_thr":
            ret, mask = cv.threshold(gray, self.thr1, 255, cv.THRESH_BINARY)
        elif self.method == "double_thr":
            thr_min = min(self.thr1, self.thr2)
            thr_max = max(self.thr1, self.thr2)
            ret1, threshold1 = cv.threshold(gray, thr_min, 255, cv.THRESH_BINARY)
            ret2, threshold2 = cv.threshold(gray, thr_max, 255, cv.THRESH_BINARY_INV)
            mask = np.bitwise_and(threshold1, threshold2)
        elif self.method == "triangle":
            ret, mask = cv.threshold(gray, 0, 255, cv.THRESH_TRIANGLE)
        elif self.method == "adaptive":
            mask = cv.adaptiveThreshold(
                gray,
                255,
                self.kernel_mode,
                cv.THRESH_BINARY,
                self.kernel_size,
                self.offset,
            )

        sample.image = mask
        return sample


class InRangeThreshold(AbstractTransform):

    def __init__(
        self,
        low_h_thr: int = 0,
        low_s_thr: int = 0,
        low_v_thr: int = 0,
        high_h_thr: int = 180,
        high_s_thr: int = 30,
        high_v_thr: int = 255,
    ) -> None:
        """InRangeThreshold, HSV颜色范围分割, 颜色变换

        Args:
            low_h_thr: HJue low threshold, 色相(H)下限, (0, 180, 1], 0
            low_s_thr: Saturation low threshold, 饱和度(S)下限, (0, 255, 1], 0
            low_v_thr: Value low threshold, 亮度(V)下限, (0, 255, 1], 0
            high_h_thr: Hue high threshold, 色相(H)上限, (0, 180, 1], 180
            high_s_thr: Saturation high threshold, 饱和度(S)上限, (0, 255, 1], 255
            high_v_thr: Value high threshold, 亮度(V)上限, (0, 255, 1], 255
        """
        super().__init__(use_gpu=False)

        self.low_thr = (low_h_thr, low_s_thr, low_v_thr)
        self.high_thr = (high_h_thr, high_s_thr, high_v_thr)

    def _apply(self, sample):
        if sample.image is None:
            return sample

        image_hsv = cv.cvtColor(sample.image, cv.COLOR_RGB2HSV)
        image = cv.inRange(image_hsv, self.low_thr, self.high_thr)
        sample.image = np.repeat(image[..., np.newaxis], repeats=3, axis=-1)

        return sample


class BarCodeMask(AbstractTransform):
    # @liying50
    def __init__(
            self,
            threshold: float = 180,
            min_area: int = 100
        ) -> None:
        """BarCodeMask, 条形码剔除, 图像掩膜

        Args:
            threshold: Threshold, 图像阈值, [0.0, 255.0, 0.1], 180
            min_area: Minimal area, 最小剔除面积, [0, 100000, 1], 100
        """
        super().__init__(use_gpu=False)
        self.thr = threshold
        self.min_area = min_area

    def _apply(self, sample):
        if sample.image is None:
            return sample

        # 转换为灰度图并进行高斯模糊处理
        image_blurred = cv.GaussianBlur(rgb_to_gray(sample.image), (51, 51), 0)

        # 应用阈值处理
        _, mask = cv.threshold(image_blurred, self.thr, 255, cv.THRESH_BINARY)

        # 查找轮廓并过滤小于指定面积的轮廓
        contours, _ = cv.findContours(
            mask.astype(np.uint8), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
        )
        bounding_boxes = [
            cv.boundingRect(cnt)
            for cnt in contours
            if cv.contourArea(cnt) > self.min_area
        ]
        if bounding_boxes:
            # 创建二进制掩码并应用外接矩形
            binary_mask = np.ones(sample.image.shape, dtype=np.uint8)
            for x, y, w, h in bounding_boxes:
                binary_mask[y : y + h, x : x + w] = 0
            # 更新样本图像
            sample.image *= binary_mask
        return sample


class DateCodeMask(AbstractTransform):
    def __init__(
        self,
        rotate: bool = True,
        use_gpu: bool = True,
        date_code_year: int = 25,
        slice_horizontal_stride: int = 4000,
        slice_vertical_stride: int = 1550,
        slice_merge_x_thres: int = 2300,
        slice_merge_y_thres: int = 80,
    ) -> None:
        """DateCodeMask, 年周号屏蔽, 图像掩膜

        Args:
            rotate: Rotate, 是否顺时针旋转图像90度, {'True', 'False'}, 'True'
            use_gpu: Use gpu, 检测年周号是否使用gpu, {'True', 'False'}, 'True'
            date_code_year: Date code year, 年周号的年份, (23, 27], 25
            slice_horizontal_stride: Slice horizontal stride, 切片的水平步长, (0, 32000, 1], 800
            slice_vertical_stride: Slice vertical stride, 切片的垂直步长, (0, 32000, 1], 2000
            slice_merge_x_thres: Slice merge x threshold, x方向合并阈值, (0, 32000, 1], 100
            slice_merge_y_thres: Slice merge y threshold, y方向合并阈值, (0, 32000, 1], 20
        """
        super().__init__(use_gpu=False)
        self.date_code_list = [f"{week:02d}{date_code_year}" for week in range(1, 54)]
        self.date_code_list.extend([f"{week:02d}{date_code_year+1}" for week in range(1, 54)])
        self.rotate = eval_arg(rotate, None)
        use_gpu = eval_arg(use_gpu, None)
        self.ppocr = PPOCR(
            use_angle_cls=False,
            lang="en",
            det=True,
            rec=True,
            use_gpu=use_gpu,
            slice_horizontal_stride=slice_horizontal_stride,
            slice_vertical_stride=slice_vertical_stride,
            slice_merge_x_thres=slice_merge_x_thres,
            slice_merge_y_thres=slice_merge_y_thres,
        )
        image = np.zeros((512, 512, 3))
        doc = {'image': image}
        res = self.ppocr(doc)

    def _apply(self, sample):
        if sample.image is None:
            return sample
        if self.rotate:
            sample.image = cv.rotate(sample.image, cv.ROTATE_90_CLOCKWISE)
        res = self.ppocr(sample)
        # 过滤出文本在data_code_list中的info
        filtered_infos = []
        for info in res.ocr:
            text = info['text']
            four_digit_numbers = re.findall(r'\d{4}', text) # list
            if any(num in self.date_code_list for num in four_digit_numbers):
                total_chars = len(text)
                if total_chars > 4:
                    match = re.search(four_digit_numbers[0], text)
                    start_idx = match.start(0)
                    end_idx = match.end(0)
                    pos = info['position']
                    x_left = pos[0][0]    # 左上 x
                    x_right = pos[1][0]   # 右上 x
                    y_top = pos[0][1]     # 左上 y
                    y_bottom = pos[2][1]  # 右下 y
                    # 线性映射字符索引到 x 坐标
                    def idx_to_x(idx):
                        return x_left + (x_right - x_left) * (idx / total_chars)
                    x_start = idx_to_x(start_idx)
                    x_end = idx_to_x(end_idx)
                    new_position = [
                        [int(x_start), y_top],
                        [int(x_end), y_top],
                        [int(x_end), y_bottom],
                        [int(x_start), y_bottom]
                    ]
                    info['position'] = new_position
                filtered_infos.append(info)

        if filtered_infos:
            mask = np.ones_like(sample.image, dtype=np.uint8)
            for info in filtered_infos:
                polygon_points = np.array(info["position"], dtype=np.int32)
                cv.fillPoly(mask, [polygon_points], 0)
                masked_image = sample.image * mask
                sample.image = masked_image
        if self.rotate:
            sample.image = cv.rotate(sample.image, cv.ROTATE_90_COUNTERCLOCKWISE)

        return sample


class ColorLineDefectDetect(AbstractTransform):
    # @liying50
    def __init__(
            self,
            threshold: float = 220.0,
            min_blob_area: float = 150.0,
            max_allowed_gap: int = 80,
            height_width_ratio: float = 1.5,
            auto_detect_line: bool = False
        ) -> None:
        """ColorLineDefectDetect, 色线缺失检测, 缺陷检测

        Args:
            threshold: Threshold, 图像阈值, [0.0, 255.0, 0.1], 220.0
            min_blob_area: MinBlobArea, 最小连通域面积, [0.0, 300, 0.1], 150.0
            max_allowed_gap: MaxAllowedGap, 允许的最大间隙, [0, 1000, 1], 80
            height_width_ratio: HeightWidthRatio, 色线高宽比, [0.0, 10.0], 1.5
            auto_detect_line: AutoDetectLine, 自动检测色线, {'True', 'False'}, 'False'
        """
        super().__init__(use_gpu=False)
        self.thr = threshold  # 二值化阈值：色线非常亮，背景很暗，高阈值可以有效分离
        self.min_blob_area = min_blob_area  # 最小连通域面积：用于过滤太小的噪点
        self.max_allowed_gap = max_allowed_gap  # 允许的最大间隙（像素）。超过此值的断裂被视为缺陷。正常胎纹沟槽引起的断裂应该小于这个值。
        self.height_width_ratio = height_width_ratio
        self.auto_detect_line = eval_arg(auto_detect_line, None)

    def _detect_color_line(
            self, 
            roi_x_start: int, 
            roi_x_end: int, 
            img_h: int, 
            gray_image: np.ndarray
        ) -> List[List[Tuple[int, int]]]:
        """在指定 ROI 内检测色线断裂缺陷，返回缺陷框 [(x1,y1), (x2,y2)] 列表"""

        roi_image = gray_image[:, roi_x_start: roi_x_end]

        # 二值化处理
        _, binary_mask = cv.threshold(roi_image, self.thr, 255, cv.THRESH_BINARY)
        # 形态学开运算去噪
        kernel = np.ones((3,3), np.uint8)
        binary_mask = cv.morphologyEx(binary_mask, cv.MORPH_OPEN, kernel, iterations=1)

        # 连通域分析 (Find Blobs), 找出ROI中所有独立的白色区域
        num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(binary_mask, connectivity=8)
        # 收集有效的线段 Blob
        line_segments = []
        LineSegment = namedtuple('LineSegment', ['y', 'height', 'x', 'width'])
        for i in range(1, num_labels): # 从1开始，跳过背景(0)
            area = stats[i, cv.CC_STAT_AREA]
            height = stats[i, cv.CC_STAT_HEIGHT]
            width = stats[i, cv.CC_STAT_WIDTH]    
            # 过滤逻辑：
            # 1. 面积要足够大（过滤噪点）
            # 2. 形状应该是细长的（高度远大于宽度），这是色线的特征
            if area > self.min_blob_area and height > (width * self.height_width_ratio):
                # 保存关键信息：y坐标, 高度, x坐标, 宽度
                x = stats[i, cv.CC_STAT_LEFT]
                y = stats[i, cv.CC_STAT_TOP]
                line_segments.append(LineSegment(y, height, x, width))

        defect_boxes = []        
        # 如果找到少于2段线段，无法计算间隙，直接返回
        if len(line_segments) < 2:
            return defect_boxes

        # 关键步骤：按垂直位置 (y坐标) 对线段进行排序，确保从上到下处理
        line_segments.sort(key=lambda seg: seg.y) 

        # 判断第一条线段顶部与图像顶部的间隙
        first = line_segments[0]
        top_gap = first.y  # 第一条线段顶部y坐标即为与图像顶部的距离
        if top_gap > self.max_allowed_gap:
            box_x = roi_x_start + first.x
            box_w = first.width
            box_top_left = (box_x, 0)  # 缺陷框从图像顶部开始
            box_bottom_right = (box_x + box_w, first.y)
            defect_boxes.append([box_top_left, box_bottom_right])

        # 遍历排序后的线段，比较相邻两段之间的距离
        for i in range(len(line_segments) - 1):
            curr = line_segments[i]
            nxt = line_segments[i + 1]

            # 计算间隙：下一段的顶部Y - 当前段的底部Y
            gap = nxt.y - (curr.y + curr.height)
        
            # 判定：如果间隙大于设定的阈值，则为缺陷
            if gap > self.max_allowed_gap:            
                # 框的范围是：上方线段的底部 到 下方线段的顶部
                box_x = roi_x_start + min(curr.x, nxt.x) # 取较左侧的X作为起点
                box_w = max(curr.x + curr.width, nxt.x + nxt.width) - min(curr.x, nxt.x)
                box_top_left = (box_x, curr.y + curr.height)
                box_bottom_right = (box_x + box_w, nxt.y)
                defect_boxes.append([box_top_left, box_bottom_right])
        
        # 检查最后一条线段与图像底部的间隙
        last = line_segments[-1]
        bottom_gap = img_h - (last.y + last.height)
        if bottom_gap > self.max_allowed_gap:
            box_x = roi_x_start + last.x
            box_w = last.width
            box_top_left = (box_x, last.y + last.height)
            box_bottom_right = (box_x + box_w, img_h)
            defect_boxes.append([box_top_left, box_bottom_right])
        return defect_boxes

    def _apply(self, sample):
        if sample.image is None:
            return sample

        gray = rgb_to_gray(sample.image)
        img_h, img_w = gray.shape
        binary_mask = np.zeros_like(gray)

        bounding_boxes = []
        if self.auto_detect_line:  # TODO: 需要优化
            step = img_w // 5  # 将胎冠区域按照水平方向拆分5等份，默认色线在第2份或者第4份范围内
            left_roi_x_start = step
            left_roi_x_end = 2 * step
            right_roi_x_start = 3 * step
            right_roi_x_end = 4 * step
            left_defect = self._detect_color_line(
                roi_x_start=left_roi_x_start, 
                roi_x_end=left_roi_x_end,
                img_h=img_h,
                gray_image=gray
            )
            right_defect = self._detect_color_line(
                roi_x_start=right_roi_x_start, 
                roi_x_end=right_roi_x_end, 
                img_h=img_h, 
                gray_image=gray
            )  
            if left_defect or right_defect:
                bounding_boxes = left_defect + right_defect   
        else:
            bounding_boxes = self._detect_color_line(
                roi_x_start=0, 
                roi_x_end=img_w, 
                img_h=img_h, 
                gray_image=gray
                )         
        if bounding_boxes:
            for top_left, bottom_right in bounding_boxes:
                x1, y1 = top_left
                x2, y2 = bottom_right
                x1 = max(0, min(x1, img_w))
                x2 = max(0, min(x2, img_w))
                y1 = max(0, min(y1, img_h))
                y2 = max(0, min(y2, img_h))
                if x2 > x1 and y2 > y1:
                    binary_mask[y1:y2, x1:x2] = 255   
        sample.image = binary_mask
        return sample
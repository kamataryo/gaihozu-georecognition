#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import numpy
import cv2
from line_detector import detect_lines

def get_corners(map_path):

    lines = detect_lines(map_path)

    if lines is None:
        return []
    else:
        print(f"Detected {len(lines)} lines.")

    """
    直線を4本に絞るため近接する直線の組み合わせをすべて取得。
    直線は番号で表される。
    """
    deletion_indexes = []
    for indexed_line1 in enumerate(lines):
        for indexed_line2 in enumerate(lines):
            if indexed_line1[0] != indexed_line2[0]:
                line1 = indexed_line1[1][0]
                line2 = indexed_line2[1][0]
                rho1 = line1[0]
                theta1 = line1[1]
                rho2 = line2[0]
                theta2 = line2[1]
                "rhoの差が100以内かつthetaの差がπ/18の時に近接していると定義。"
                if abs(rho1 - rho2) < 500 and abs(theta1 - theta2) < numpy.pi/18:
                    deletion_indexes.append([indexed_line1[0], indexed_line2[0]])


    "近接する直線を近接グループに分ける。"
    merged_indexes = ["hoge"]
    for deletion_set in deletion_indexes:
        counter = 0
        for i, merged_set in enumerate(merged_indexes):
            if set(deletion_set).intersection(merged_set):
                merged_indexes[i] = merged_indexes[i] + deletion_set
                break
            counter = counter + 1
            if counter == len(merged_indexes):
                merged_indexes.append(deletion_set)

    merged_indexes = merged_indexes[1:]

    index_groups = [list(set(i)) for i in merged_indexes]  # 各グループの直線番号の重複を除去。


    sides1 = [i[0] for i in index_groups]  # 各グループから直線を1本ずつ取得。残りは捨てる。

    "近接するすべての直線を取得。"
    grouped_indexes = []
    for sublist in index_groups:
        for element in sublist:
            grouped_indexes.append(element)

    "すべての直線と近接する直線の差をとる。つまり近接する直線のない独立した直線を取得。"
    sides2 = list(set(list(range(len(lines)))).difference(grouped_indexes))

    sides = [lines[i] for i in sides1 + sides2]  # 辺となる4直線の番号のリスト。

    "4直線の傾きとy軸との交点を取得。"
    slopes = []
    intersections = []
    for side in sides:
        side = side[0]
        slope = -(1/numpy.tan(side[1]))
        slopes.append(slope)
        intersection = side[0] * 1/numpy.sin(side[1])
        intersections.append(intersection)

    xysides = list(zip(slopes, intersections))  # y = ax + bで表される直線のaとbのリスト。
    xyrtsides = list(zip(xysides, sides))  # 4辺のa, b, rho, thetaのリスト。

    "4辺の交点4つの座標を取得。"
    corners = []
    for two_sides in itertools.combinations(xyrtsides, 2):
        side1 = two_sides[0]
        side2 = two_sides[1]
        xyside1 = side1[0]
        xyside2 = side2[0]
        rtside1 = side1[1][0]
        rtside2 = side2[1][0]
        if xyside1[0] == xyside2[0]:
            pass
        else:
            if not numpy.isfinite(xyside1[0]):
                x = rtside1[0]
                y = xyside2[0]*x + xyside2[1]
            elif not numpy.isfinite(xyside2[0]):
                x = rtside2[0]
                y = xyside1[0]*x + xyside1[1]
            else:
                x = - (xyside2[1] - xyside1[1]) / (xyside2[0] - xyside1[0])
                y = xyside1[0] + xyside1[1]
            x = int(x)
            y = int(y)
            corners.append([x, y])

    if len(corners) > 0:

        x_average = sum([x for (x, y) in corners])/len(corners)
        y_average = sum([y for (x, y) in corners])/len(corners)

        for corner in corners:
            if corner[0] > x_average and corner[1] > y_average:
                lower_right = corner
            elif corner[0] > x_average and corner[1] < y_average:
                upper_right = corner
            elif corner[0] < x_average and corner[1] > y_average:
                lower_left = corner
            elif corner[1] < x_average and corner[1] < y_average:
                upper_left = corner
            else:
                return None
        '''
        upper_left = min(corners, key=sum)  # 左上の頂点の座標。
        lower_right = max(corners, key=sum)  # 右下の頂点の座標。
        '''

        "外側の太い枠から内側の細い枠まで頂点の座標を縦横へ210ピクセルずらす。"
        upper_left = [element + 210 for element in upper_left]

        upper_right[0] = upper_right[0] - 210
        upper_right[1] = upper_right[1] + 210
        lower_left[0] = lower_left[0] + 210
        lower_left[1] = lower_left[1] - 210

        lower_right = [element - 210 for element in lower_right]

        shifted_corners = [upper_left, upper_right, lower_left, lower_right]

    else:
        return None

    if len(corners) == 4:
        return shifted_corners
    else:
        return None



import os

files = os.listdir("./samples/")
for i, file in enumerate(files):
  if not file.endswith(".jpg"):
    continue
  map_path = "./samples/" + file
  corners = get_corners(map_path)
  if corners is None:
      print(f"{i+1}/{len(files)}: {file} -> No corners found")
  else:
    print(f"{i+1}/{len(files)}: {file}" + " -> " + str(corners))

# 画像の読み込みと矩形の描画を行うためのコードは以下の通りです。

# color = cv2.imread(map_path, 1)  # 地図をカラーで読み込む。
# color = cv2.rectangle(color, tuple(corners[0]), tuple(corners[3]), (0, 0, 255), 50)  # 矩形を描画。
# cv2.imshow("window_name", color)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


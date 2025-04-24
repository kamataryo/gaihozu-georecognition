#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This script contains a function which detects straight lines in a gaihozu map that are possible four sides of the inner map.
'''

map_path = "gomanbunnoichichikeizu343.jpg"

def detect_lines(map_path, binary_threshold = 100, erode_kernel = 3, erode_iteration = 2, line_accumulation = 10000, rho_precision = 2, theta_precision = numpy.pi/90):

    '''
    パラメーター説明。
    BINARY_THRESHOLD = 100  # 二値画像変換の閾値。
    ERODE_KERNEL = 3  # erodeのkernelの大きさ
    ERODE_ITERATION = 2 # erodeの実行回数
    LINE_ACCUMULATION = 10000  # 直線として認識されるのに必要な同一直線状のpx数。←違う？
    RHO_PRECISION = 2
    THETA_PRECISION = numpy.pi/90
'''

    import numpy
    import cv2

    gray = cv2.imread(map_path, 0)  # 画像の読み込み。第2引数を0にするとグレースケール。

    "二値画像へ変換。1つ目の戻り値 (retへ代入) は無視。"
    ret, thresh = cv2.threshold(gray, binary_threshold, 255,
                                cv2.THRESH_BINARY_INV)

    kernel = numpy.ones((erode_kernel, erode_kernel), numpy.uint8)  # erodeのkernel。
    eroded = cv2.erode(thresh, kernel, iterations=erode_iteration)  # 境界を削り細線を除去。

    """
    辺の候補となる直線 (極座標表示) を取得。
    引数は対象画像、ρの精度、θの精度、線分の閾値。
    この時点で直線の数は4本より多い。
    """
    lines = cv2.HoughLines(thresh, rho_precision, theta_precision,
                           line_accumulation)

    return lines

lines = detect_lines(map_path)

import cv2

'検出した直線をすべて描画する。'
color = cv2.imread(map_path, 1)
for line in lines:
    line = line[0]
    rho = line[0]
    theta = line[1]
    a = numpy.cos(theta)
    b = numpy.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 20000*(-b))
    y1 = int(y0 + 20000*(a))
    x2 = int(x0 - 20000*(-b))
    y2 = int(y0 - 20000*(a))
    cv2.line(color,(x1,y1),(x2,y2),(0,0,255),50)

"""
cv2.imshow("map_path", color)
cv2.waitKey(0)
cv2.destroyAllWindows()
"""


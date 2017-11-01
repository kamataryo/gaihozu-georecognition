#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy
import cv2

# パラメーター
binary_threshold = 100 # 二値画像変換の閾値。
erode_kernel = 3 # erodeのkernelの大きさ
erode_iterations = 3 # erodeの回数
line_accumulation = 7000 # 直線として認識されるのに必要な同一直線状のpx数。
rho_precision = 4
theta_precision = numpy.pi/90


def preprocess(map_file_name):

    gray = cv2.imread(map_file_name, 0) #画像の読み込み。第2引数を0にするとグレースケールとして読み込む。

    #denoised = cv2.fastNlMeansDenoising(gray) #ノイズ除去。時間がかかる。

    #x, y, w, h = cv2.boundingRect(converted) #余白と紙の境界を検出。
    #color = cv2.imread(map_file_name, 1)
    #cv2.rectangle(color, (x, y), (x+w, y+h), (0,255,0), 50)

    ret, thresh = cv2.threshold(gray, binary_threshold, 255, cv2.THRESH_BINARY_INV) # 二値画像へ変換。1つ目の戻り値 (retへ代入) は無視してよい。

    #height, width  = gray.shape
    #noframe = cv2.rectangle(thresh, (0, 0), (width, height), (0, 0, 0), 1000) #画像の左上、右下の点を基準とする太さ1500pxの長方形を描画。マージンを塗りつぶすため。

    kernel = numpy.ones((erode_kernel, erode_kernel), numpy.uint8) #erodeのkernelを設定。
    eroded = cv2.erode(thresh, kernel, iterations = erode_iterations) #図中の境界を削る。細い線を除去して太い枠だけを残すため。
    #kernel = numpy.ones((3, 3), numpy.uint8) #erodeのkernelを設定。
    #eroded = cv2.erode(eroded, kernel, iterations = 3) #図中の境界を削る。細い線を除去して太い枠だけを残すため。

    #cv2.imshow("map", eroded)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    return eroded

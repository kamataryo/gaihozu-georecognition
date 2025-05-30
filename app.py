#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import os
import base64
import io
from line_detector import detect_lines

def determine_orientation(line):
    """
    線の向き（縦/横）を判定する関数
    """
    rho, theta = line[0]
    # theta が π/4 より小さいか、3π/4 より大きい場合は縦向き
    # それ以外は横向き
    return 'vertical' if (theta < np.pi/4 or theta > 3*np.pi/4) else 'horizontal'

def offset_line(line, offset_percentage, image_width, image_height, orientation):
    """
    線をオフセットさせる関数
    """
    rho, theta = line[0]
    # 画像サイズに基づいてオフセット量を計算
    max_offset = min(image_width, image_height) * 0.3  # 最大30%までオフセット可能
    offset_amount = max_offset * (offset_percentage / 100.0)

    # 向きに応じてオフセット方向を決定
    if orientation == 'vertical':
        # 縦線の場合、内側に向かってオフセット
        # 画像の中心からの距離に基づいて方向を決定
        center_x = image_width / 2
        line_x = rho * np.cos(theta)
        if line_x > center_x:
            # 右側の線は左に（内側に）オフセット
            new_rho = rho - offset_amount
        else:
            # 左側の線は右に（内側に）オフセット
            new_rho = rho + offset_amount
    else:
        # 横線の場合、内側に向かってオフセット
        # 画像の中心からの距離に基づいて方向を決定
        center_y = image_height / 2
        line_y = rho * np.sin(theta)
        if line_y > center_y:
            # 下側の線は上に（内側に）オフセット
            new_rho = rho - offset_amount
        else:
            # 上側の線は下に（内側に）オフセット
            new_rho = rho + offset_amount

    return np.array([[new_rho, theta]])

def draw_line_full_extent(image, line, color, thickness=3):
    """
    線を画像の端から端まで描画する関数
    元の描画方法を使用して、十分に長い線を描画
    """
    rho, theta = line[0]
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho

    # 元の方法を使用：十分に長い線を描画
    # 画像サイズに関係なく、十分に長い線を描画することで
    # 画像の境界で自然に切り取られる
    extension = 2000  # 十分に大きな値
    x1 = int(x0 + extension * (-b))
    y1 = int(y0 + extension * (a))
    x2 = int(x0 - extension * (-b))
    y2 = int(y0 - extension * (a))

    cv2.line(image, (x1, y1), (x2, y2), color, thickness)

def group_similar_lines(lines):
    """
    類似した直線をグループ化する関数
    corner_getter.pyのロジックを参考にした実装
    """
    if lines is None or len(lines) == 0:
        return []

    # 近接する直線の組み合わせを取得
    deletion_indexes = []
    for i, line1 in enumerate(lines):
        for j, line2 in enumerate(lines):
            if i != j:
                rho1, theta1 = line1[0]
                rho2, theta2 = line2[0]
                # rhoの差が500以内かつthetaの差がπ/18以内の時に近接していると定義
                if abs(rho1 - rho2) < 500 and abs(theta1 - theta2) < np.pi/18:
                    deletion_indexes.append([i, j])

    # 近接する直線を近接グループに分ける
    merged_indexes = []
    for deletion_set in deletion_indexes:
        merged = False
        for i, merged_set in enumerate(merged_indexes):
            if set(deletion_set).intersection(set(merged_set)):
                merged_indexes[i] = list(set(merged_indexes[i] + deletion_set))
                merged = True
                break
        if not merged:
            merged_indexes.append(deletion_set)

    # 各グループの重複を除去
    index_groups = [list(set(group)) for group in merged_indexes]

    # グループ化された直線のインデックスを取得
    grouped_indexes = set()
    for group in index_groups:
        grouped_indexes.update(group)

    # 独立した直線（グループに属さない直線）を追加
    independent_lines = []
    for i in range(len(lines)):
        if i not in grouped_indexes:
            independent_lines.append([i])

    # 全てのグループを結合
    all_groups = index_groups + independent_lines

    return all_groups

app = Flask(__name__)
CORS(app)

@app.route('/api/images', methods=['GET'])
def get_images():
    """サンプル画像のリストを取得"""
    targets_dir = './targets'
    images = []
    if os.path.exists(targets_dir):
        for file in os.listdir(targets_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(file)
    return jsonify({'images': sorted(images)})

@app.route('/api/process', methods=['POST'])
def process_image():
    """画像処理を実行"""
    try:
        data = request.json
        image_name = data.get('image_name')
        params = data.get('parameters', {})

        # パラメータの取得（デフォルト値を設定）
        binary_threshold = params.get('binary_threshold', 100)
        erode_kernel = params.get('erode_kernel', 3)
        erode_iteration = params.get('erode_iteration', 2)
        line_accumulation = params.get('line_accumulation', 10000)
        rho_precision = params.get('rho_precision', 2)
        theta_precision = params.get('theta_precision', np.pi/90)
        line_offset = params.get('line_offset', 0)  # デフォルト値は0（オフセットなし）

        # 画像パスの構築
        image_path = os.path.join('./targets', image_name)

        if not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404

        # 画像を読み込み
        original_image = cv2.imread(image_path)
        if original_image is None:
            return jsonify({'error': 'Failed to load image'}), 400

        # detect_lines関数を実行
        lines = detect_lines(
            image_path,
            binary_threshold=binary_threshold,
            erode_kernel=erode_kernel,
            erode_iteration=erode_iteration,
            line_accumulation=line_accumulation,
            rho_precision=rho_precision,
            theta_precision=theta_precision
        )

        # 結果画像を作成（元の画像に線を重ねる）
        result_image = original_image.copy()

        if lines is not None:
            # 直線をグループ化する
            line_groups = group_similar_lines(lines)

            # グループごとに異なる色で描画
            colors = [
                (0, 0, 255),    # 赤
                (0, 255, 0),    # 緑
                (255, 0, 0),    # 青
                (0, 255, 255),  # 黄
                (255, 0, 255),  # マゼンタ
                (255, 255, 0),  # シアン
                (128, 0, 128),  # 紫
                (255, 165, 0),  # オレンジ
            ]

            # 画像サイズを取得
            image_height, image_width = result_image.shape[:2]

            for group_idx, group in enumerate(line_groups):
                color = colors[group_idx % len(colors)]
                for line_idx in group:
                    line = lines[line_idx]

                    # オフセット処理を適用
                    if line_offset > 0:
                        orientation = determine_orientation(line)
                        line = offset_line(line, line_offset, image_width, image_height, orientation)

                    # 線を画像の端から端まで描画
                    draw_line_full_extent(result_image, line, color, 3)

        # 画像をbase64エンコード
        _, buffer = cv2.imencode('.jpg', result_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_base64}',
            'lines_count': len(lines) if lines is not None else 0,
            'groups_count': len(line_groups) if lines is not None else 0
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """メインページを表示"""
    return send_file('index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """静的ファイルを配信"""
    return send_file(filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

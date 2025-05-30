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
    samples_dir = './samples'
    images = []
    if os.path.exists(samples_dir):
        for file in os.listdir(samples_dir):
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

        # 画像パスの構築
        image_path = os.path.join('./samples', image_name)

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

            for group_idx, group in enumerate(line_groups):
                color = colors[group_idx % len(colors)]
                for line_idx in group:
                    line = lines[line_idx]
                    rho, theta = line[0]
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    x1 = int(x0 + 1000 * (-b))
                    y1 = int(y0 + 1000 * (a))
                    x2 = int(x0 - 1000 * (-b))
                    y2 = int(y0 - 1000 * (a))
                    cv2.line(result_image, (x1, y1), (x2, y2), color, 3)

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

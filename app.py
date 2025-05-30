#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import os
import base64
import io
import csv
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
    extension = 20000  # 十分に大きな値
    x1 = int(x0 + extension * (-b))
    y1 = int(y0 + extension * (a))
    x2 = int(x0 - extension * (-b))
    y2 = int(y0 - extension * (a))

    cv2.line(image, (x1, y1), (x2, y2), color, thickness)

def calculate_representative_lines(line_groups, lines):
    """
    各グループの代表線を計算する関数
    グループ内の全ての線のrhoとthetaの平均を取る
    """
    representative_lines = []

    for group in line_groups:
        if not group:  # 空のグループをスキップ
            continue

        # グループ内の全ての線のrhoとthetaを集める
        rhos = []
        thetas = []
        for line_idx in group:
            rho, theta = lines[line_idx][0]
            rhos.append(rho)
            thetas.append(theta)

        # 平均を計算
        avg_rho = sum(rhos) / len(rhos)
        avg_theta = sum(thetas) / len(thetas)

        representative_lines.append(np.array([[avg_rho, avg_theta]]))

    return representative_lines

def compute_intersection(line1, line2):
    """
    2つの線の交点を計算する関数
    line1, line2: [rho, theta] 形式の線のパラメータ
    """
    rho1, theta1 = line1
    rho2, theta2 = line2

    # 平行線の場合は交点なし
    if abs(theta1 - theta2) < 1e-10 or abs(abs(theta1 - theta2) - np.pi) < 1e-10:
        return None

    # 線の方程式の係数を計算
    a1 = np.cos(theta1)
    b1 = np.sin(theta1)
    a2 = np.cos(theta2)
    b2 = np.sin(theta2)

    # 連立方程式を解いて交点を計算
    det = a1 * b2 - a2 * b1
    if abs(det) < 1e-10:  # 行列式がほぼ0なら平行
        return None

    x = (b2 * rho1 - b1 * rho2) / det
    y = (-a2 * rho1 + a1 * rho2) / det

    return (int(x), int(y))

def calculate_intersections(line_groups, lines):
    """
    グループ化された線同士の交点を計算する関数
    """
    # 各グループの代表線を計算
    representative_lines = calculate_representative_lines(line_groups, lines)

    intersections = []
    # 全ての代表線の組み合わせについて交点を計算
    for i, line1 in enumerate(representative_lines):
        for j, line2 in enumerate(representative_lines):
            if i < j:  # 重複を避けるため、i < j の組み合わせのみ処理
                intersection = compute_intersection(line1[0], line2[0])
                if intersection:
                    intersections.append(intersection)

    return intersections

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

            # グループ数が10を超える場合はエラーを返す
            if len(line_groups) > 10:
                return jsonify({
                    'error': 'グループ数が多すぎます（最大10個まで）。パラメータを調整してグループ数を減らしてください。',
                    'groups_count': len(line_groups)
                }), 400  # Bad Request ステータスコード

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

            # オフセットが適用された線の代表線を計算して交点を求める
            offset_representative_lines = []
            for group in line_groups:
                if not group:  # 空のグループをスキップ
                    continue

                # グループ内の全ての線のrhoとthetaを集める（オフセット適用後）
                rhos = []
                thetas = []
                for line_idx in group:
                    line = lines[line_idx]

                    # オフセット処理を適用
                    if line_offset > 0:
                        orientation = determine_orientation(line)
                        line = offset_line(line, line_offset, image_width, image_height, orientation)

                    rho, theta = line[0]
                    rhos.append(rho)
                    thetas.append(theta)

                # 平均を計算
                avg_rho = sum(rhos) / len(rhos)
                avg_theta = sum(thetas) / len(thetas)

                offset_representative_lines.append(np.array([[avg_rho, avg_theta]]))

            # オフセット適用後の代表線同士の交点を計算
            intersections = []
            for i, line1 in enumerate(offset_representative_lines):
                for j, line2 in enumerate(offset_representative_lines):
                    if i < j:  # 重複を避けるため、i < j の組み合わせのみ処理
                        intersection = compute_intersection(line1[0], line2[0])
                        if intersection:
                            intersections.append(intersection)

            # 交点を画像上に描画
            for point in intersections:
                # 交点が画像の範囲内にある場合のみ描画
                if 0 <= point[0] < image_width and 0 <= point[1] < image_height:
                    cv2.circle(result_image, point, 10, (255, 255, 255), -1)  # 白い円で交点を描画
                    cv2.circle(result_image, point, 10, (0, 0, 0), 2)  # 黒い輪郭線

        # 画像をbase64エンコード
        _, buffer = cv2.imencode('.jpg', result_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_base64}',
            'lines_count': len(lines) if lines is not None else 0,
            'groups_count': len(line_groups) if lines is not None else 0,
            'intersections_count': len(intersections) if lines is not None else 0
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-all', methods=['POST'])
def process_all_images():
    """すべての画像の交点を計算してCSVとして出力"""
    try:
        data = request.json
        params = data.get('parameters', {})

        # パラメータの取得（デフォルト値を設定）
        binary_threshold = params.get('binary_threshold', 100)
        erode_kernel = params.get('erode_kernel', 3)
        erode_iteration = params.get('erode_iteration', 2)
        line_accumulation = params.get('line_accumulation', 10000)
        rho_precision = params.get('rho_precision', 2)
        theta_precision = params.get('theta_precision', np.pi/90)
        line_offset = params.get('line_offset', 0)

        # 画像リストを取得
        targets_dir = './targets'
        images = []
        if os.path.exists(targets_dir):
            for file in os.listdir(targets_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    images.append(file)

        # 結果を格納するリスト
        results = []

        # 各画像に対して処理を実行
        for image_name in images:
            try:
                image_path = os.path.join('./targets', image_name)

                # 画像を読み込み
                original_image = cv2.imread(image_path)
                if original_image is None:
                    # 画像読み込みエラー
                    result = [image_name] + [''] * 8 + ['画像の読み込みに失敗しました']
                    results.append(result)
                    continue

                # 画像サイズを取得
                image_height, image_width = original_image.shape[:2]

                # 線を検出
                lines = detect_lines(
                    image_path,
                    binary_threshold=binary_threshold,
                    erode_kernel=erode_kernel,
                    erode_iteration=erode_iteration,
                    line_accumulation=line_accumulation,
                    rho_precision=rho_precision,
                    theta_precision=theta_precision
                )

                if lines is None or len(lines) == 0:
                    # 線が検出されなかった
                    result = [image_name] + [''] * 8 + ['線が検出されませんでした']
                    results.append(result)
                    continue

                # 直線をグループ化
                line_groups = group_similar_lines(lines)

                if len(line_groups) > 10:
                    # グループ数が多すぎる
                    result = [image_name] + [''] * 8 + [f'グループ数が多すぎます（{len(line_groups)}個）']
                    results.append(result)
                    continue

                # オフセット適用後の代表線を計算
                offset_representative_lines = []
                for group in line_groups:
                    if not group:  # 空のグループをスキップ
                        continue

                    # グループ内の全ての線のrhoとthetaを集める（オフセット適用後）
                    rhos = []
                    thetas = []
                    for line_idx in group:
                        line = lines[line_idx]

                        # オフセット処理を適用
                        if line_offset > 0:
                            orientation = determine_orientation(line)
                            line = offset_line(line, line_offset, image_width, image_height, orientation)

                        rho, theta = line[0]
                        rhos.append(rho)
                        thetas.append(theta)

                    # 平均を計算
                    avg_rho = sum(rhos) / len(rhos)
                    avg_theta = sum(thetas) / len(thetas)

                    offset_representative_lines.append(np.array([[avg_rho, avg_theta]]))

                # 交点を計算
                intersections = []
                for i, line1 in enumerate(offset_representative_lines):
                    for j, line2 in enumerate(offset_representative_lines):
                        if i < j:  # 重複を避けるため、i < j の組み合わせのみ処理
                            intersection = compute_intersection(line1[0], line2[0])
                            if intersection:
                                intersections.append(intersection)

                if len(intersections) != 4:
                    # 交点が4つでない
                    result = [image_name] + [''] * 8 + [f'交点が4つではありません（{len(intersections)}個）']
                    results.append(result)
                    continue

                # 交点を左上、右上、左下、右下の順に並べ替え
                x_coords = [p[0] for p in intersections]
                y_coords = [p[1] for p in intersections]
                x_avg = sum(x_coords) / 4
                y_avg = sum(y_coords) / 4

                sorted_intersections = [None] * 4
                for point in intersections:
                    x, y = point
                    if x < x_avg and y < y_avg:  # 左上
                        sorted_intersections[0] = point
                    elif x > x_avg and y < y_avg:  # 右上
                        sorted_intersections[1] = point
                    elif x < x_avg and y > y_avg:  # 左下
                        sorted_intersections[2] = point
                    else:  # 右下
                        sorted_intersections[3] = point

                # Noneがある場合（並べ替えに失敗した場合）
                if None in sorted_intersections:
                    result = [image_name] + [''] * 8 + ['交点の並べ替えに失敗しました']
                    results.append(result)
                    continue

                # 結果をリストに追加（成功）
                result = [image_name]
                for point in sorted_intersections:
                    result.extend(point)
                result.append('')  # エラーなし
                results.append(result)

            except Exception as e:
                # 処理中に例外が発生した場合
                result = [image_name] + [''] * 8 + [f'処理中にエラーが発生しました: {str(e)}']
                results.append(result)

        # CSVファイルを作成
        csv_path = 'intersections.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # ヘッダーを書き込み
            writer.writerow(['画像ファイル名', 'x0', 'y0', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'error'])
            # データを書き込み
            writer.writerows(results)

        # 成功と失敗の数をカウント
        success_count = sum(1 for result in results if result[-1] == '')

        return jsonify({
            'success': True,
            'message': f'全{len(results)}個の画像を処理し、うち{success_count}画像の交点を計算しました。CSVファイルに保存しました。',
            'csv_path': csv_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/csv-preview', methods=['GET'])
def get_csv_preview():
    """CSVファイルのプレビューを取得"""
    try:
        csv_path = 'intersections.csv'
        if not os.path.exists(csv_path):
            return jsonify({'error': 'CSVファイルが見つかりません'}), 404

        # CSVファイルを読み込み
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        if len(rows) == 0:
            return jsonify({'error': 'CSVファイルが空です'}), 400

        # ヘッダーとデータを分離
        headers = rows[0] if len(rows) > 0 else []
        data = rows[1:] if len(rows) > 1 else []

        # 最大100行まで表示
        preview_data = data[:100]

        return jsonify({
            'success': True,
            'headers': headers,
            'data': preview_data,
            'total_rows': len(data),
            'preview_rows': len(preview_data)
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

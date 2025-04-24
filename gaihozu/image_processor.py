"""画像処理機能を提供するモジュール。

このモジュールは、外邦図の画像から図郭の四隅を検出するための機能を提供します。
"""

from typing import List, Optional, Tuple

import cv2
import numpy as np


class ImageProcessor:
    """外邦図の画像処理を行うクラス。"""

    def __init__(
        self,
        binary_threshold: int = 100,
        erode_kernel: int = 3,
        erode_iteration: int = 2,
        line_accumulation: int = 10000,
        rho_precision: int = 2,
        theta_precision: float = np.pi / 90,
    ):
        """ImageProcessorを初期化します。

        Args:
            binary_threshold: 二値画像変換の閾値
            erode_kernel: erodeのkernelの大きさ
            erode_iteration: erodeの実行回数
            line_accumulation: 直線として認識されるのに必要な同一直線状のpx数
            rho_precision: ρの精度
            theta_precision: θの精度
        """
        self.binary_threshold = binary_threshold
        self.erode_kernel = erode_kernel
        self.erode_iteration = erode_iteration
        self.line_accumulation = line_accumulation
        self.rho_precision = rho_precision
        self.theta_precision = theta_precision

    def detect_lines(self, image_path: str) -> Optional[np.ndarray]:
        """画像から直線を検出します。

        Args:
            image_path: 画像ファイルのパス

        Returns:
            検出された直線のリスト、検出できなかった場合はNone
        """
        try:
            # 画像の読み込み（グレースケール）
            gray = cv2.imread(image_path, 0)
            if gray is None:
                print(f"画像を読み込めませんでした: {image_path}")
                return None

            # 二値画像へ変換
            _, thresh = cv2.threshold(
                gray, self.binary_threshold, 255, cv2.THRESH_BINARY_INV
            )

            # 境界を削り細線を除去
            kernel = np.ones((self.erode_kernel, self.erode_kernel), np.uint8)
            eroded = cv2.erode(thresh, kernel, iterations=self.erode_iteration)

            # 辺の候補となる直線（極座標表示）を取得
            lines = cv2.HoughLines(
                eroded,
                self.rho_precision,
                self.theta_precision,
                self.line_accumulation,
            )

            return lines
        except Exception as e:
            print(f"直線検出中にエラーが発生しました: {e}")
            return None

    def get_corners(self, image_path: str) -> Optional[List[List[int]]]:
        """画像から図郭の四隅の座標を検出します。

        Args:
            image_path: 画像ファイルのパス

        Returns:
            検出された四隅の座標のリスト、検出できなかった場合はNone
            座標は [左上, 右上, 左下, 右下] の順
        """
        lines = self.detect_lines(image_path)
        if lines is None:
            return None

        # 近接する直線の組み合わせをすべて取得
        deletion_indexes = []
        for i, line1 in enumerate(lines):
            for j, line2 in enumerate(lines):
                if i != j:
                    rho1, theta1 = line1[0]
                    rho2, theta2 = line2[0]
                    # rhoの差が500以内かつthetaの差がπ/18の時に近接していると定義
                    if abs(rho1 - rho2) < 500 and abs(theta1 - theta2) < np.pi / 18:
                        deletion_indexes.append([i, j])

        # 近接する直線を近接グループに分ける
        merged_indexes = []
        for deletion_set in deletion_indexes:
            for i, merged_set in enumerate(merged_indexes):
                if set(deletion_set).intersection(merged_set):
                    merged_indexes[i] = list(set(merged_indexes[i] + deletion_set))
                    break
            else:
                merged_indexes.append(deletion_set)

        # 各グループから直線を1本ずつ取得
        sides1 = [group[0] for group in merged_indexes if group]

        # 近接するすべての直線を取得
        grouped_indexes = []
        for sublist in merged_indexes:
            for element in sublist:
                grouped_indexes.append(element)

        # 近接する直線のない独立した直線を取得
        sides2 = list(set(range(len(lines))).difference(grouped_indexes))

        # 辺となる直線を取得
        sides = [lines[i] for i in sides1 + sides2]

        # 4辺の傾きとy軸との交点を取得
        xysides = []
        for side in sides:
            rho, theta = side[0]
            if np.sin(theta) == 0:  # 垂直線の場合
                slope = float('inf')
                intersection = rho
            else:
                slope = -(np.cos(theta) / np.sin(theta))
                intersection = rho / np.sin(theta)
            xysides.append((slope, intersection, rho, theta))

        # 4辺の交点を計算
        corners = []
        for i, side1 in enumerate(xysides):
            for side2 in enumerate(xysides[i + 1:], i + 1):
                slope1, intercept1, rho1, theta1 = side1
                slope2, intercept2, rho2, theta2 = side2[1]

                # 平行線の場合はスキップ
                if slope1 == slope2:
                    continue

                # 交点の計算
                if np.isinf(slope1):
                    x = intercept1
                    y = slope2 * x + intercept2
                elif np.isinf(slope2):
                    x = intercept2
                    y = slope1 * x + intercept1
                else:
                    x = (intercept2 - intercept1) / (slope1 - slope2)
                    y = slope1 * x + intercept1

                corners.append([int(x), int(y)])

        if len(corners) < 4:
            print("四隅を検出できませんでした。")
            return None

        # 四隅の座標を左上、右上、左下、右下の順に並べ替え
        x_coords = [corner[0] for corner in corners]
        y_coords = [corner[1] for corner in corners]
        x_center = sum(x_coords) / len(corners)
        y_center = sum(y_coords) / len(corners)

        upper_left = None
        upper_right = None
        lower_left = None
        lower_right = None

        for corner in corners:
            x, y = corner
            if x < x_center and y < y_center:
                upper_left = corner
            elif x > x_center and y < y_center:
                upper_right = corner
            elif x < x_center and y > y_center:
                lower_left = corner
            elif x > x_center and y > y_center:
                lower_right = corner

        # 四隅が全て検出できなかった場合
        if None in [upper_left, upper_right, lower_left, lower_right]:
            print("四隅を正しく分類できませんでした。")
            return None

        # 外側の太い枠から内側の細い枠まで頂点の座標を縦横へ調整
        # 注: この値は画像によって調整が必要かもしれません
        margin = 210
        upper_left = [upper_left[0] + margin, upper_left[1] + margin]
        upper_right = [upper_right[0] - margin, upper_right[1] + margin]
        lower_left = [lower_left[0] + margin, lower_left[1] - margin]
        lower_right = [lower_right[0] - margin, lower_right[1] - margin]

        return [upper_left, upper_right, lower_left, lower_right]

    def visualize_corners(
        self, image_path: str, corners: List[List[int]], output_path: str
    ) -> bool:
        """検出された四隅を可視化した画像を生成します。

        Args:
            image_path: 元画像のパス
            corners: 四隅の座標 [左上, 右上, 左下, 右下]
            output_path: 出力画像のパス

        Returns:
            処理が成功したかどうか
        """
        try:
            # 画像をカラーで読み込む
            image = cv2.imread(image_path, 1)
            if image is None:
                print(f"画像を読み込めませんでした: {image_path}")
                return False

            # 四隅を結ぶ線を描画
            color = (0, 0, 255)  # 赤色 (BGR)
            thickness = 5

            # 上辺
            cv2.line(image, tuple(corners[0]), tuple(corners[1]), color, thickness)
            # 右辺
            cv2.line(image, tuple(corners[1]), tuple(corners[3]), color, thickness)
            # 下辺
            cv2.line(image, tuple(corners[2]), tuple(corners[3]), color, thickness)
            # 左辺
            cv2.line(image, tuple(corners[0]), tuple(corners[2]), color, thickness)

            # 四隅に点を描画
            for corner in corners:
                cv2.circle(image, tuple(corner), 10, color, -1)

            # 画像を保存
            cv2.imwrite(output_path, image)
            return True
        except Exception as e:
            print(f"可視化中にエラーが発生しました: {e}")
            return False

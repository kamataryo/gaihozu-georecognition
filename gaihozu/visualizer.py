"""可視化機能を提供するモジュール。

このモジュールは、GCPと図郭を可視化するための機能を提供します。
"""

from typing import Dict, List, Tuple, Union

import cv2
import numpy as np


class Visualizer:
    """GCPと図郭を可視化するクラス。"""

    def __init__(self):
        """Visualizerを初期化します。"""
        pass

    def visualize_gcp(
        self,
        image_path: str,
        gcp_list: List[Dict[str, Union[str, List[float], List[int]]]],
        output_path: str,
    ) -> bool:
        """GCPを可視化した画像を生成します。

        Args:
            image_path: 元画像のパス
            gcp_list: GCPのリスト
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

            # GCPを描画
            for gcp in gcp_list:
                pixel = gcp["pixel"]
                world = gcp["world"]

                # GCPの位置に点を描画
                cv2.circle(image, tuple(pixel), 10, (0, 0, 255), -1)

                # GCPのIDと座標を描画
                text = f"ID: {gcp['id']}, Lat: {world[1]:.6f}, Lon: {world[0]:.6f}"
                cv2.putText(
                    image,
                    text,
                    (pixel[0] + 15, pixel[1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                    cv2.LINE_AA,
                )

            # 画像を保存
            cv2.imwrite(output_path, image)
            return True
        except Exception as e:
            print(f"GCPの可視化中にエラーが発生しました: {e}")
            return False

    def visualize_grid(
        self,
        image_path: str,
        corners: List[List[int]],
        coordinates: List[Tuple[float, float]],
        output_path: str,
        grid_size: int = 10,
    ) -> bool:
        """図郭と緯度経度グリッドを可視化した画像を生成します。

        Args:
            image_path: 元画像のパス
            corners: 画像の四隅の座標 [左上, 右上, 左下, 右下]
            coordinates: 対応する緯度経度 [(左上緯度, 左上経度), (右上緯度, 右上経度),
                                      (左下緯度, 左下経度), (右下緯度, 右下経度)]
            output_path: 出力画像のパス
            grid_size: グリッドの分割数

        Returns:
            処理が成功したかどうか
        """
        try:
            # 画像をカラーで読み込む
            image = cv2.imread(image_path, 1)
            if image is None:
                print(f"画像を読み込めませんでした: {image_path}")
                return False

            # 図郭を描画
            color = (0, 0, 255)  # 赤色 (BGR)
            thickness = 2

            # 上辺
            cv2.line(image, tuple(corners[0]), tuple(corners[1]), color, thickness)
            # 右辺
            cv2.line(image, tuple(corners[1]), tuple(corners[3]), color, thickness)
            # 下辺
            cv2.line(image, tuple(corners[2]), tuple(corners[3]), color, thickness)
            # 左辺
            cv2.line(image, tuple(corners[0]), tuple(corners[2]), color, thickness)

            # 四隅の座標を描画
            for i, (corner, coord) in enumerate(zip(corners, coordinates)):
                text = f"({coord[0]:.6f}, {coord[1]:.6f})"
                cv2.putText(
                    image,
                    text,
                    (corner[0], corner[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1,
                    cv2.LINE_AA,
                )

            # グリッドを描画
            grid_color = (0, 255, 0)  # 緑色 (BGR)
            grid_thickness = 1

            # 水平方向のグリッド線
            for i in range(1, grid_size):
                ratio = i / grid_size
                # 左辺上の点
                left_x = int(corners[0][0] + (corners[2][0] - corners[0][0]) * ratio)
                left_y = int(corners[0][1] + (corners[2][1] - corners[0][1]) * ratio)
                # 右辺上の点
                right_x = int(corners[1][0] + (corners[3][0] - corners[1][0]) * ratio)
                right_y = int(corners[1][1] + (corners[3][1] - corners[1][1]) * ratio)
                # 線を描画
                cv2.line(image, (left_x, left_y), (right_x, right_y), grid_color, grid_thickness)

                # 緯度を計算
                lat = coordinates[0][0] + (coordinates[2][0] - coordinates[0][0]) * ratio
                # 緯度を描画
                cv2.putText(
                    image,
                    f"{lat:.6f}",
                    (corners[0][0] - 80, left_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    grid_color,
                    1,
                    cv2.LINE_AA,
                )

            # 垂直方向のグリッド線
            for i in range(1, grid_size):
                ratio = i / grid_size
                # 上辺上の点
                top_x = int(corners[0][0] + (corners[1][0] - corners[0][0]) * ratio)
                top_y = int(corners[0][1] + (corners[1][1] - corners[0][1]) * ratio)
                # 下辺上の点
                bottom_x = int(corners[2][0] + (corners[3][0] - corners[2][0]) * ratio)
                bottom_y = int(corners[2][1] + (corners[3][1] - corners[2][1]) * ratio)
                # 線を描画
                cv2.line(image, (top_x, top_y), (bottom_x, bottom_y), grid_color, grid_thickness)

                # 経度を計算
                lon = coordinates[0][1] + (coordinates[1][1] - coordinates[0][1]) * ratio
                # 経度を描画
                cv2.putText(
                    image,
                    f"{lon:.6f}",
                    (top_x, corners[0][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    grid_color,
                    1,
                    cv2.LINE_AA,
                )

            # 画像を保存
            cv2.imwrite(output_path, image)
            return True
        except Exception as e:
            print(f"グリッドの可視化中にエラーが発生しました: {e}")
            return False

    def create_demo_image(
        self,
        image_path: str,
        corners: List[List[int]],
        coordinates: List[Tuple[float, float]],
        output_path: str,
    ) -> bool:
        """デモ画像を生成します。

        この関数は、GCPと図郭を可視化したデモ画像を生成します。

        Args:
            image_path: 元画像のパス
            corners: 画像の四隅の座標 [左上, 右上, 左下, 右下]
            coordinates: 対応する緯度経度 [(左上緯度, 左上経度), (右上緯度, 右上経度),
                                      (左下緯度, 左下経度), (右下緯度, 右下経度)]
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

            # 図郭を描画
            color = (0, 0, 255)  # 赤色 (BGR)
            thickness = 3

            # 上辺
            cv2.line(image, tuple(corners[0]), tuple(corners[1]), color, thickness)
            # 右辺
            cv2.line(image, tuple(corners[1]), tuple(corners[3]), color, thickness)
            # 下辺
            cv2.line(image, tuple(corners[2]), tuple(corners[3]), color, thickness)
            # 左辺
            cv2.line(image, tuple(corners[0]), tuple(corners[2]), color, thickness)

            # 四隅に点を描画
            for i, (corner, coord) in enumerate(zip(corners, coordinates)):
                # GCPの位置に点を描画
                cv2.circle(image, tuple(corner), 10, color, -1)

                # GCPの座標を描画
                text = f"GCP{i+1}: ({coord[0]:.6f}, {coord[1]:.6f})"
                text_position = (
                    corner[0] + 15 if corner[0] < image.shape[1] // 2 else corner[0] - 250,
                    corner[1] + 15 if corner[1] < image.shape[0] // 2 else corner[1] - 15
                )
                cv2.putText(
                    image,
                    text,
                    text_position,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2,
                    cv2.LINE_AA,
                )

            # タイトルを描画
            title = "外邦図 GCP デモ画像"
            cv2.putText(
                image,
                title,
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (255, 0, 0),
                3,
                cv2.LINE_AA,
            )

            # 画像を保存
            cv2.imwrite(output_path, image)
            return True
        except Exception as e:
            print(f"デモ画像の生成中にエラーが発生しました: {e}")
            return False

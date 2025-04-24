"""GCP（Ground Control Points）生成機能を提供するモジュール。

このモジュールは、画像の四隅の座標と対応する緯度経度から、GCPを生成する機能を提供します。
"""

import json
from typing import Dict, List, Tuple, Union

import cv2
import numpy as np


class GcpGenerator:
    """GCPを生成するクラス。"""

    def __init__(self):
        """GcpGeneratorを初期化します。"""
        pass

    def generate_gcp(
        self,
        corners: List[List[int]],
        coordinates: List[Tuple[float, float]],
    ) -> List[Dict[str, Union[str, List[float], List[int]]]]:
        """画像の四隅の座標と対応する緯度経度からGCPを生成します。

        Args:
            corners: 画像の四隅の座標 [左上, 右上, 左下, 右下]
            coordinates: 対応する緯度経度 [(左上緯度, 左上経度), (右上緯度, 右上経度),
                                      (左下緯度, 左下経度), (右下緯度, 右下経度)]

        Returns:
            GCPのリスト
        """
        if len(corners) != 4 or len(coordinates) != 4:
            raise ValueError("corners と coordinates はそれぞれ4つの要素が必要です")

        gcp_list = []
        for i, (corner, coord) in enumerate(zip(corners, coordinates)):
            gcp = {
                "id": f"gcp{i+1}",
                "pixel": corner,
                "world": [coord[1], coord[0]],  # [経度, 緯度] の順
            }
            gcp_list.append(gcp)

        return gcp_list

    def save_gcp(self, gcp_list: List[Dict], output_path: str) -> bool:
        """GCPをJSONファイルとして保存します。

        Args:
            gcp_list: GCPのリスト
            output_path: 出力ファイルのパス

        Returns:
            保存が成功したかどうか
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(gcp_list, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"GCPの保存中にエラーが発生しました: {e}")
            return False

    def transform_point(
        self,
        pixel_x: int,
        pixel_y: int,
        corners: List[List[int]],
        coordinates: List[Tuple[float, float]],
    ) -> Tuple[float, float]:
        """画像上の点の座標を地理座標に変換します。

        この関数は、アフィン変換を使用して画像上の点の座標を地理座標に変換します。

        Args:
            pixel_x: 画像上のX座標
            pixel_y: 画像上のY座標
            corners: 画像の四隅の座標 [左上, 右上, 左下, 右下]
            coordinates: 対応する緯度経度 [(左上緯度, 左上経度), (右上緯度, 右上経度),
                                      (左下緯度, 左下経度), (右下緯度, 右下経度)]

        Returns:
            変換された地理座標 (緯度, 経度)
        """
        # 画像の四隅の座標
        src_points = np.array(corners, dtype=np.float32)

        # 対応する地理座標（経度、緯度の順）
        dst_points = np.array(
            [
                [coordinates[0][1], coordinates[0][0]],  # 左上（経度, 緯度）
                [coordinates[1][1], coordinates[1][0]],  # 右上（経度, 緯度）
                [coordinates[2][1], coordinates[2][0]],  # 左下（経度, 緯度）
                [coordinates[3][1], coordinates[3][0]],  # 右下（経度, 緯度）
            ],
            dtype=np.float32,
        )

        # 射影変換行列を計算
        transform_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

        # 点を変換
        point = np.array([[pixel_x, pixel_y]], dtype=np.float32)
        transformed_point = cv2.perspectiveTransform(
            point.reshape(-1, 1, 2), transform_matrix
        )

        # 結果を (緯度, 経度) の形式で返す
        return (float(transformed_point[0][0][1]), float(transformed_point[0][0][0]))

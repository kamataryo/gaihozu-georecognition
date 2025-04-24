"""Visualizerクラスのテスト。"""

import os
import unittest
from unittest.mock import MagicMock, patch

import cv2
import numpy as np

from gaihozu.visualizer import Visualizer


class TestVisualizer(unittest.TestCase):
    """Visualizerクラスのテスト。"""

    def setUp(self):
        """テストの前処理。"""
        self.visualizer = Visualizer()
        self.test_image_path = "test_image.jpg"
        self.output_path = "test_output.jpg"
        self.corners = [[10, 10], [90, 10], [10, 90], [90, 90]]
        self.coordinates = [(35.0, 139.0), (35.0, 140.0), (34.0, 139.0), (34.0, 140.0)]
        self.gcp_list = [
            {"id": "gcp1", "pixel": [10, 10], "world": [139.0, 35.0]},
            {"id": "gcp2", "pixel": [90, 10], "world": [140.0, 35.0]},
            {"id": "gcp3", "pixel": [10, 90], "world": [139.0, 34.0]},
            {"id": "gcp4", "pixel": [90, 90], "world": [140.0, 34.0]},
        ]

    def tearDown(self):
        """テストの後処理。"""
        # テスト画像が存在する場合は削除
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    @patch("cv2.imread")
    @patch("cv2.circle")
    @patch("cv2.putText")
    @patch("cv2.imwrite")
    def test_visualize_gcp(self, mock_imwrite, mock_put_text, mock_circle, mock_imread):
        """visualize_gcp メソッドのテスト。"""
        # モックの設定
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_imwrite.return_value = True

        # テスト実行
        result = self.visualizer.visualize_gcp(
            self.test_image_path, self.gcp_list, self.output_path
        )

        # 検証
        mock_imread.assert_called_once_with(self.test_image_path, 1)
        self.assertEqual(mock_circle.call_count, 4)  # 4つのGCPを描画
        self.assertEqual(mock_put_text.call_count, 4)  # 4つのテキストを描画
        mock_imwrite.assert_called_once_with(self.output_path, mock_image)
        self.assertTrue(result)

    @patch("cv2.imread")
    def test_visualize_gcp_image_not_found(self, mock_imread):
        """画像が見つからない場合のvisualize_gcpメソッドのテスト。"""
        # モックの設定
        mock_imread.return_value = None

        # テスト実行
        result = self.visualizer.visualize_gcp(
            self.test_image_path, self.gcp_list, self.output_path
        )

        # 検証
        mock_imread.assert_called_once_with(self.test_image_path, 1)
        self.assertFalse(result)

    @patch("cv2.imread")
    @patch("cv2.line")
    @patch("cv2.putText")
    @patch("cv2.imwrite")
    def test_visualize_grid(self, mock_imwrite, mock_put_text, mock_line, mock_imread):
        """visualize_grid メソッドのテスト。"""
        # モックの設定
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_imwrite.return_value = True
        grid_size = 5

        # テスト実行
        result = self.visualizer.visualize_grid(
            self.test_image_path, self.corners, self.coordinates, self.output_path, grid_size
        )

        # 検証
        mock_imread.assert_called_once_with(self.test_image_path, 1)
        # 4辺 + (grid_size-1)*2 本のグリッド線
        self.assertEqual(mock_line.call_count, 4 + (grid_size - 1) * 2)
        # 4つの角の座標 + (grid_size-1)*2 個のグリッド座標
        self.assertEqual(mock_put_text.call_count, 4 + (grid_size - 1) * 2)
        mock_imwrite.assert_called_once_with(self.output_path, mock_image)
        self.assertTrue(result)

    @patch("cv2.imread")
    def test_visualize_grid_image_not_found(self, mock_imread):
        """画像が見つからない場合のvisualize_gridメソッドのテスト。"""
        # モックの設定
        mock_imread.return_value = None

        # テスト実行
        result = self.visualizer.visualize_grid(
            self.test_image_path, self.corners, self.coordinates, self.output_path
        )

        # 検証
        mock_imread.assert_called_once_with(self.test_image_path, 1)
        self.assertFalse(result)

    @patch("cv2.imread")
    @patch("cv2.line")
    @patch("cv2.circle")
    @patch("cv2.putText")
    @patch("cv2.imwrite")
    def test_create_demo_image(
        self, mock_imwrite, mock_put_text, mock_circle, mock_line, mock_imread
    ):
        """create_demo_image メソッドのテスト。"""
        # モックの設定
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_imwrite.return_value = True

        # テスト実行
        result = self.visualizer.create_demo_image(
            self.test_image_path, self.corners, self.coordinates, self.output_path
        )

        # 検証
        mock_imread.assert_called_once_with(self.test_image_path, 1)
        self.assertEqual(mock_line.call_count, 4)  # 4辺を描画
        self.assertEqual(mock_circle.call_count, 4)  # 4つの角を描画
        self.assertEqual(mock_put_text.call_count, 5)  # 4つのGCP座標 + タイトル
        mock_imwrite.assert_called_once_with(self.output_path, mock_image)
        self.assertTrue(result)

    @patch("cv2.imread")
    def test_create_demo_image_image_not_found(self, mock_imread):
        """画像が見つからない場合のcreate_demo_imageメソッドのテスト。"""
        # モックの設定
        mock_imread.return_value = None

        # テスト実行
        result = self.visualizer.create_demo_image(
            self.test_image_path, self.corners, self.coordinates, self.output_path
        )

        # 検証
        mock_imread.assert_called_once_with(self.test_image_path, 1)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

"""GcpGeneratorクラスのテスト。"""

import json
import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

import cv2
import numpy as np

from gaihozu.gcp_generator import GcpGenerator


class TestGcpGenerator(unittest.TestCase):
    """GcpGeneratorクラスのテスト。"""

    def setUp(self):
        """テストの前処理。"""
        self.gcp_generator = GcpGenerator()
        self.corners = [[10, 10], [90, 10], [10, 90], [90, 90]]
        self.coordinates = [(35.0, 139.0), (35.0, 140.0), (34.0, 139.0), (34.0, 140.0)]
        self.output_path = "test_gcp.json"

    def tearDown(self):
        """テストの後処理。"""
        # テスト出力ファイルが存在する場合は削除
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_generate_gcp(self):
        """generate_gcp メソッドのテスト。"""
        # テスト実行
        gcp_list = self.gcp_generator.generate_gcp(self.corners, self.coordinates)

        # 検証
        self.assertEqual(len(gcp_list), 4)
        for i, gcp in enumerate(gcp_list):
            self.assertEqual(gcp["id"], f"gcp{i+1}")
            self.assertEqual(gcp["pixel"], self.corners[i])
            self.assertEqual(gcp["world"], [self.coordinates[i][1], self.coordinates[i][0]])

    def test_generate_gcp_invalid_input(self):
        """無効な入力に対するgenerate_gcpメソッドのテスト。"""
        # 無効な入力
        invalid_corners = [[10, 10], [90, 10], [10, 90]]  # 3つしかない
        invalid_coordinates = [(35.0, 139.0), (35.0, 140.0), (34.0, 139.0)]  # 3つしかない

        # テスト実行と検証
        with self.assertRaises(ValueError):
            self.gcp_generator.generate_gcp(invalid_corners, self.coordinates)

        with self.assertRaises(ValueError):
            self.gcp_generator.generate_gcp(self.corners, invalid_coordinates)

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_gcp(self, mock_json_dump, mock_file_open):
        """save_gcp メソッドのテスト。"""
        # テストデータ
        gcp_list = [
            {"id": "gcp1", "pixel": [10, 10], "world": [139.0, 35.0]},
            {"id": "gcp2", "pixel": [90, 10], "world": [140.0, 35.0]},
            {"id": "gcp3", "pixel": [10, 90], "world": [139.0, 34.0]},
            {"id": "gcp4", "pixel": [90, 90], "world": [140.0, 34.0]},
        ]

        # テスト実行
        result = self.gcp_generator.save_gcp(gcp_list, self.output_path)

        # 検証
        mock_file_open.assert_called_once_with(self.output_path, "w", encoding="utf-8")
        mock_json_dump.assert_called_once()
        self.assertTrue(result)

    @patch("builtins.open")
    def test_save_gcp_exception(self, mock_file_open):
        """例外が発生した場合のsave_gcpメソッドのテスト。"""
        # モックの設定
        mock_file_open.side_effect = IOError("テスト用のIOエラー")

        # テストデータ
        gcp_list = [
            {"id": "gcp1", "pixel": [10, 10], "world": [139.0, 35.0]},
        ]

        # テスト実行
        result = self.gcp_generator.save_gcp(gcp_list, self.output_path)

        # 検証
        mock_file_open.assert_called_once_with(self.output_path, "w", encoding="utf-8")
        self.assertFalse(result)

    @patch("cv2.getPerspectiveTransform")
    @patch("cv2.perspectiveTransform")
    def test_transform_point(self, mock_perspective_transform, mock_get_perspective_transform):
        """transform_point メソッドのテスト。"""
        # モックの設定
        mock_transform_matrix = np.eye(3)
        mock_get_perspective_transform.return_value = mock_transform_matrix

        transformed_point = np.array([[[140.0, 35.0]]], dtype=np.float32)
        mock_perspective_transform.return_value = transformed_point

        # テスト実行
        result = self.gcp_generator.transform_point(50, 50, self.corners, self.coordinates)

        # 検証
        mock_get_perspective_transform.assert_called_once()
        mock_perspective_transform.assert_called_once()
        self.assertEqual(result, (35.0, 140.0))


if __name__ == "__main__":
    unittest.main()

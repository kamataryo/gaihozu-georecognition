"""CLIモジュールのテスト。"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import cv2
import numpy as np

from gaihozu.cli import main, parse_coordinates


class TestCli(unittest.TestCase):
    """CLIモジュールのテスト。"""

    def setUp(self):
        """テストの前処理。"""
        self.test_image_path = "test_image.jpg"
        self.gcp_output_path = "test_gcp.json"
        self.demo_output_path = "test_demo.jpg"
        self.corners = [[10, 10], [90, 10], [10, 90], [90, 90]]
        self.coordinates = [(35.0, 139.0), (35.0, 140.0), (34.0, 139.0), (34.0, 140.0)]

    def tearDown(self):
        """テストの後処理。"""
        # テストファイルが存在する場合は削除
        for path in [self.test_image_path, self.gcp_output_path, self.demo_output_path]:
            if os.path.exists(path):
                os.remove(path)

    def test_parse_coordinates(self):
        """parse_coordinates 関数のテスト。"""
        # 正常なケース
        coord_str = "35.123,139.456"
        result = parse_coordinates(coord_str)
        self.assertEqual(result, (35.123, 139.456))

        # 無効なケース
        invalid_coord_str = "35.123"
        with self.assertRaises(ValueError):
            parse_coordinates(invalid_coord_str)

        invalid_coord_str = "35.123,139.456,0.0"
        with self.assertRaises(ValueError):
            parse_coordinates(invalid_coord_str)

        invalid_coord_str = "invalid,139.456"
        with self.assertRaises(ValueError):
            parse_coordinates(invalid_coord_str)

    @patch("sys.argv", ["gaihozu", "--version"])
    @patch("gaihozu.cli.__version__", "0.1.0")
    @patch("builtins.print")
    def test_main_version(self, mock_print):
        """--version オプションのテスト。"""
        # テスト実行
        result = main()

        # 検証
        mock_print.assert_called_once_with("gaihozu-georecognition version 0.1.0")
        self.assertEqual(result, 0)

    @patch("sys.argv", ["gaihozu"])
    @patch("argparse.ArgumentParser.print_help")
    def test_main_no_command(self, mock_print_help):
        """コマンドなしの場合のテスト。"""
        # テスト実行
        result = main()

        # 検証
        mock_print_help.assert_called_once()
        self.assertEqual(result, 1)

    @patch(
        "sys.argv",
        [
            "gaihozu",
            "process",
            "nonexistent.jpg",
            "--ul",
            "35.0,139.0",
            "--ur",
            "35.0,140.0",
            "--ll",
            "34.0,139.0",
            "--lr",
            "34.0,140.0",
        ],
    )
    @patch("builtins.print")
    def test_main_process_file_not_found(self, mock_print):
        """存在しないファイルを処理しようとした場合のテスト。"""
        # テスト実行
        result = main()

        # 検証
        mock_print.assert_called_with(f"エラー: 画像ファイルが見つかりません: nonexistent.jpg")
        self.assertEqual(result, 1)

    @patch(
        "sys.argv",
        [
            "gaihozu",
            "process",
            "test_image.jpg",
            "--ul",
            "invalid",
            "--ur",
            "35.0,140.0",
            "--ll",
            "34.0,139.0",
            "--lr",
            "34.0,140.0",
        ],
    )
    @patch("os.path.isfile")
    @patch("builtins.print")
    def test_main_process_invalid_coordinates(self, mock_print, mock_isfile):
        """無効な座標形式の場合のテスト。"""
        # モックの設定
        mock_isfile.return_value = True

        # テスト実行
        result = main()

        # 検証
        mock_print.assert_called_with("エラー: 無効な座標形式です: invalid。正しい形式は '緯度,経度' です。")
        self.assertEqual(result, 1)

    @patch(
        "sys.argv",
        [
            "gaihozu",
            "process",
            "test_image.jpg",
            "--ul",
            "35.0,139.0",
            "--ur",
            "35.0,140.0",
            "--ll",
            "34.0,139.0",
            "--lr",
            "34.0,140.0",
            "--gcp-output",
            "test_gcp.json",
            "--demo-output",
            "test_demo.jpg",
            "--no-auto-detect",
        ],
    )
    @patch("os.path.isfile")
    @patch("cv2.imread")
    @patch("gaihozu.gcp_generator.GcpGenerator.generate_gcp")
    @patch("gaihozu.gcp_generator.GcpGenerator.save_gcp")
    @patch("gaihozu.visualizer.Visualizer.create_demo_image")
    @patch("builtins.print")
    def test_main_process_success(
        self,
        mock_print,
        mock_create_demo_image,
        mock_save_gcp,
        mock_generate_gcp,
        mock_imread,
        mock_isfile,
    ):
        """正常に処理が完了する場合のテスト。"""
        # モックの設定
        mock_isfile.return_value = True
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_generate_gcp.return_value = [{"id": "gcp1", "pixel": [10, 10], "world": [139.0, 35.0]}]
        mock_save_gcp.return_value = True
        mock_create_demo_image.return_value = True

        # テスト実行
        result = main()

        # 検証
        mock_isfile.assert_called_once_with("test_image.jpg")
        mock_imread.assert_called_once()
        mock_generate_gcp.assert_called_once()
        mock_save_gcp.assert_called_once_with(
            [{"id": "gcp1", "pixel": [10, 10], "world": [139.0, 35.0]}], "test_gcp.json"
        )
        mock_create_demo_image.assert_called_once()
        mock_print.assert_called_with("処理が完了しました。")
        self.assertEqual(result, 0)

    @patch(
        "sys.argv",
        [
            "gaihozu",
            "process",
            "test_image.jpg",
            "--ul",
            "35.0,139.0",
            "--ur",
            "35.0,140.0",
            "--ll",
            "34.0,139.0",
            "--lr",
            "34.0,140.0",
        ],
    )
    @patch("os.path.isfile")
    @patch("gaihozu.image_processor.ImageProcessor.get_corners")
    @patch("gaihozu.gcp_generator.GcpGenerator.generate_gcp")
    @patch("gaihozu.gcp_generator.GcpGenerator.save_gcp")
    @patch("gaihozu.visualizer.Visualizer.create_demo_image")
    @patch("builtins.print")
    def test_main_process_auto_detect(
        self,
        mock_print,
        mock_create_demo_image,
        mock_save_gcp,
        mock_generate_gcp,
        mock_get_corners,
        mock_isfile,
    ):
        """自動検出モードのテスト。"""
        # モックの設定
        mock_isfile.return_value = True
        mock_get_corners.return_value = self.corners
        mock_generate_gcp.return_value = [{"id": "gcp1", "pixel": [10, 10], "world": [139.0, 35.0]}]
        mock_save_gcp.return_value = True
        mock_create_demo_image.return_value = True

        # テスト実行
        result = main()

        # 検証
        mock_isfile.assert_called_once_with("test_image.jpg")
        mock_get_corners.assert_called_once_with("test_image.jpg")
        mock_generate_gcp.assert_called_once()
        mock_save_gcp.assert_called_once()
        mock_create_demo_image.assert_called_once()
        mock_print.assert_called_with("処理が完了しました。")
        self.assertEqual(result, 0)

    @patch(
        "sys.argv",
        [
            "gaihozu",
            "process",
            "test_image.jpg",
            "--ul",
            "35.0,139.0",
            "--ur",
            "35.0,140.0",
            "--ll",
            "34.0,139.0",
            "--lr",
            "34.0,140.0",
        ],
    )
    @patch("os.path.isfile")
    @patch("gaihozu.image_processor.ImageProcessor.get_corners")
    @patch("cv2.imread")
    @patch("gaihozu.gcp_generator.GcpGenerator.generate_gcp")
    @patch("gaihozu.gcp_generator.GcpGenerator.save_gcp")
    @patch("gaihozu.visualizer.Visualizer.create_demo_image")
    @patch("builtins.print")
    def test_main_process_auto_detect_failed(
        self,
        mock_print,
        mock_create_demo_image,
        mock_save_gcp,
        mock_generate_gcp,
        mock_imread,
        mock_get_corners,
        mock_isfile,
    ):
        """自動検出が失敗した場合のテスト。"""
        # モックの設定
        mock_isfile.return_value = True
        mock_get_corners.return_value = None
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_generate_gcp.return_value = [{"id": "gcp1", "pixel": [10, 10], "world": [139.0, 35.0]}]
        mock_save_gcp.return_value = True
        mock_create_demo_image.return_value = True

        # テスト実行
        result = main()

        # 検証
        mock_isfile.assert_called_once_with("test_image.jpg")
        mock_get_corners.assert_called_once_with("test_image.jpg")
        mock_imread.assert_called_once()
        mock_generate_gcp.assert_called_once()
        mock_save_gcp.assert_called_once()
        mock_create_demo_image.assert_called_once()
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()

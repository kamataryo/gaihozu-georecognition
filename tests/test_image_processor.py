"""ImageProcessorクラスのテスト。"""

import os
import unittest
from unittest.mock import MagicMock, patch

import cv2
import numpy as np

from gaihozu.image_processor import ImageProcessor


class TestImageProcessor(unittest.TestCase):
    """ImageProcessorクラスのテスト。"""

    def setUp(self):
        """テストの前処理。"""
        self.image_processor = ImageProcessor()
        self.test_image_path = "test_image.jpg"

    def tearDown(self):
        """テストの後処理。"""
        # テスト画像が存在する場合は削除
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)

    @patch("cv2.imread")
    @patch("cv2.HoughLines")
    def test_detect_lines(self, mock_hough_lines, mock_imread):
        """detect_lines メソッドのテスト。"""
        # モックの設定
        mock_image = np.zeros((100, 100), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_lines = np.array([[[10, 0.5]], [[20, 1.0]]])
        mock_hough_lines.return_value = mock_lines

        # テスト実行
        lines = self.image_processor.detect_lines(self.test_image_path)

        # 検証
        mock_imread.assert_called_once_with(self.test_image_path, 0)
        self.assertIsNotNone(lines)
        self.assertEqual(len(lines), 2)
        np.testing.assert_array_equal(lines, mock_lines)

    @patch("cv2.imread")
    def test_detect_lines_image_not_found(self, mock_imread):
        """画像が見つからない場合のdetect_linesメソッドのテスト。"""
        # モックの設定
        mock_imread.return_value = None

        # テスト実行
        lines = self.image_processor.detect_lines(self.test_image_path)

        # 検証
        mock_imread.assert_called_once_with(self.test_image_path, 0)
        self.assertIsNone(lines)

    @patch("gaihozu.image_processor.ImageProcessor.detect_lines")
    def test_get_corners(self, mock_detect_lines):
        """get_corners メソッドのテスト。"""
        # モックの設定
        mock_lines = np.array(
            [
                [[100, 0.1]],
                [[200, 0.2]],
                [[300, 1.5]],
                [[400, 1.6]],
            ]
        )
        mock_detect_lines.return_value = mock_lines

        # テスト実行
        corners = self.image_processor.get_corners(self.test_image_path)

        # 検証
        mock_detect_lines.assert_called_once_with(self.test_image_path)
        self.assertIsNotNone(corners)
        self.assertEqual(len(corners), 4)  # 4つの角を検出

    @patch("gaihozu.image_processor.ImageProcessor.detect_lines")
    def test_get_corners_no_lines(self, mock_detect_lines):
        """直線が検出されない場合のget_cornersメソッドのテスト。"""
        # モックの設定
        mock_detect_lines.return_value = None

        # テスト実行
        corners = self.image_processor.get_corners(self.test_image_path)

        # 検証
        mock_detect_lines.assert_called_once_with(self.test_image_path)
        self.assertIsNone(corners)

    @patch("cv2.imread")
    @patch("cv2.line")
    @patch("cv2.circle")
    @patch("cv2.imwrite")
    def test_visualize_corners(self, mock_imwrite, mock_circle, mock_line, mock_imread):
        """visualize_corners メソッドのテスト。"""
        # モックの設定
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_imwrite.return_value = True
        corners = [[10, 10], [90, 10], [10, 90], [90, 90]]
        output_path = "test_output.jpg"

        # テスト実行
        result = self.image_processor.visualize_corners(
            self.test_image_path, corners, output_path
        )

        # 検証
        mock_imread.assert_called_once_with(self.test_image_path, 1)
        self.assertEqual(mock_line.call_count, 4)  # 4辺を描画
        self.assertEqual(mock_circle.call_count, 4)  # 4つの角を描画
        mock_imwrite.assert_called_once_with(output_path, mock_image)
        self.assertTrue(result)

    @patch("cv2.imread")
    def test_visualize_corners_image_not_found(self, mock_imread):
        """画像が見つからない場合のvisualize_cornersメソッドのテスト。"""
        # モックの設定
        mock_imread.return_value = None
        corners = [[10, 10], [90, 10], [10, 90], [90, 90]]
        output_path = "test_output.jpg"

        # テスト実行
        result = self.image_processor.visualize_corners(
            self.test_image_path, corners, output_path
        )

        # 検証
        mock_imread.assert_called_once_with(self.test_image_path, 1)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

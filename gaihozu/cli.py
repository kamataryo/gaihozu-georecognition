"""CLIインターフェースを提供するモジュール。

このモジュールは、コマンドライン引数を解析し、他のモジュールを呼び出して処理を実行する機能を提供します。
"""

import argparse
import os
import sys
from typing import List, Tuple

from gaihozu.gcp_generator import GcpGenerator
from gaihozu.image_processor import ImageProcessor
from gaihozu.visualizer import Visualizer


def parse_coordinates(coord_str: str) -> Tuple[float, float]:
    """緯度経度の文字列をパースします。

    Args:
        coord_str: 緯度経度の文字列（例: "35.123,139.456"）

    Returns:
        緯度と経度のタプル
    """
    try:
        lat, lon = coord_str.split(",")
        return (float(lat), float(lon))
    except ValueError:
        raise ValueError(f"無効な座標形式です: {coord_str}。正しい形式は '緯度,経度' です。")


def main() -> int:
    """CLIのエントリーポイント。

    Returns:
        終了コード
    """
    parser = argparse.ArgumentParser(
        description="外邦図の地理参照情報を生成するCLIツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  # 画像から図郭を検出し、指定した緯度経度でGCPを生成
  gaihozu process map.jpg --ul 35.123,139.456 --ur 35.123,139.789 --ll 34.987,139.456 --lr 34.987,139.789

  # 出力ファイルを指定
  gaihozu process map.jpg --ul 35.123,139.456 --ur 35.123,139.789 --ll 34.987,139.456 --lr 34.987,139.789 --gcp-output gcp.json --demo-output demo.jpg
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="サブコマンド")

    # processサブコマンド
    process_parser = subparsers.add_parser("process", help="外邦図を処理")
    process_parser.add_argument("image", help="処理する画像ファイルのパス")
    process_parser.add_argument("--ul", required=True, help="左上の緯度経度（例: 35.123,139.456）")
    process_parser.add_argument("--ur", required=True, help="右上の緯度経度（例: 35.123,139.789）")
    process_parser.add_argument("--ll", required=True, help="左下の緯度経度（例: 34.987,139.456）")
    process_parser.add_argument("--lr", required=True, help="右下の緯度経度（例: 34.987,139.789）")
    process_parser.add_argument(
        "--gcp-output", help="GCP出力ファイルのパス（デフォルト: <画像名>_gcp.json）"
    )
    process_parser.add_argument(
        "--demo-output", help="デモ画像出力ファイルのパス（デフォルト: <画像名>_demo.jpg）"
    )
    process_parser.add_argument(
        "--auto-detect",
        action="store_true",
        help="図郭を自動検出する（デフォルト: True）",
    )
    process_parser.add_argument(
        "--no-auto-detect",
        action="store_true",
        help="図郭を自動検出しない",
    )

    # バージョン表示
    parser.add_argument(
        "--version", action="store_true", help="バージョン情報を表示"
    )

    args = parser.parse_args()

    # バージョン表示
    if args.version:
        from gaihozu import __version__

        print(f"gaihozu-georecognition version {__version__}")
        return 0

    # サブコマンドが指定されていない場合はヘルプを表示
    if not args.command:
        parser.print_help()
        return 1

    # processサブコマンドの処理
    if args.command == "process":
        # 画像ファイルの存在確認
        if not os.path.isfile(args.image):
            print(f"エラー: 画像ファイルが見つかりません: {args.image}")
            return 1

        # 出力ファイルパスの設定
        image_base = os.path.splitext(args.image)[0]
        gcp_output = args.gcp_output or f"{image_base}_gcp.json"
        demo_output = args.demo_output or f"{image_base}_demo.jpg"

        # 緯度経度の解析
        try:
            ul_coord = parse_coordinates(args.ul)
            ur_coord = parse_coordinates(args.ur)
            ll_coord = parse_coordinates(args.ll)
            lr_coord = parse_coordinates(args.lr)
            coordinates = [ul_coord, ur_coord, ll_coord, lr_coord]
        except ValueError as e:
            print(f"エラー: {e}")
            return 1

        # 図郭の自動検出
        auto_detect = not args.no_auto_detect
        if auto_detect:
            print("図郭を自動検出しています...")
            image_processor = ImageProcessor()
            corners = image_processor.get_corners(args.image)
            if corners is None:
                print("警告: 図郭を自動検出できませんでした。")
                print("画像の四隅を使用します。")
                # 画像の四隅を使用
                import cv2

                image = cv2.imread(args.image)
                height, width = image.shape[:2]
                corners = [[0, 0], [width, 0], [0, height], [width, height]]
        else:
            print("図郭の自動検出をスキップします。")
            # 画像の四隅を使用
            import cv2

            image = cv2.imread(args.image)
            height, width = image.shape[:2]
            corners = [[0, 0], [width, 0], [0, height], [width, height]]

        print(f"検出された図郭の四隅: {corners}")

        # GCPの生成
        print("GCPを生成しています...")
        gcp_generator = GcpGenerator()
        gcp_list = gcp_generator.generate_gcp(corners, coordinates)
        if gcp_generator.save_gcp(gcp_list, gcp_output):
            print(f"GCPを保存しました: {gcp_output}")
        else:
            print(f"エラー: GCPの保存に失敗しました: {gcp_output}")
            return 1

        # デモ画像の生成
        print("デモ画像を生成しています...")
        visualizer = Visualizer()
        if visualizer.create_demo_image(args.image, corners, coordinates, demo_output):
            print(f"デモ画像を保存しました: {demo_output}")
        else:
            print(f"エラー: デモ画像の生成に失敗しました: {demo_output}")
            return 1

        print("処理が完了しました。")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

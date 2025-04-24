# gaihozu-georecognition

外邦図の地理参照情報を生成するCLIツール

## 概要

このツールは、外邦図（古い地図）の画像から図郭を自動検出し、指定された緯度経度情報と組み合わせてGCP（Ground Control Points）を生成します。また、検出された図郭と生成されたGCPを可視化したデモ画像も出力します。

## 特徴

- 画像処理による図郭の自動検出
- 指定された緯度経度情報とピクセル座標を対応付けたGCPの生成
- 図郭とGCPを可視化したデモ画像の生成
- Mac/Windowsの両方で動作
- モダンなPython開発環境（Poetry、Type Hints、テスト）

## インストール

### 前提条件

- Python 3.8以上
- [Poetry](https://python-poetry.org/docs/#installation)（依存関係管理ツール）

### インストール手順

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/gaihozu-georecognition.git
cd gaihozu-georecognition

# Poetryで依存関係をインストール
poetry install
```

## 使い方

### 基本的な使い方

```bash
# Poetryの仮想環境内でコマンドを実行
poetry run gaihozu process 地図画像.jpg --ul 35.123,139.456 --ur 35.123,139.789 --ll 34.987,139.456 --lr 34.987,139.789
```

または、Poetryシェルを起動してから実行することもできます：

```bash
# Poetryシェルを起動
poetry shell

# コマンドを実行
gaihozu process 地図画像.jpg --ul 35.123,139.456 --ur 35.123,139.789 --ll 34.987,139.456 --lr 34.987,139.789
```

### コマンドラインオプション

```
usage: gaihozu process [-h] --ul UL --ur UR --ll LL --lr LR [--gcp-output GCP_OUTPUT] [--demo-output DEMO_OUTPUT] [--auto-detect] [--no-auto-detect] image

positional arguments:
  image                 処理する画像ファイルのパス

optional arguments:
  -h, --help            ヘルプメッセージを表示して終了
  --ul UL               左上の緯度経度（例: 35.123,139.456）
  --ur UR               右上の緯度経度（例: 35.123,139.789）
  --ll LL               左下の緯度経度（例: 34.987,139.456）
  --lr LR               右下の緯度経度（例: 34.987,139.789）
  --gcp-output GCP_OUTPUT
                        GCP出力ファイルのパス（デフォルト: <画像名>_gcp.json）
  --demo-output DEMO_OUTPUT
                        デモ画像出力ファイルのパス（デフォルト: <画像名>_demo.jpg）
  --auto-detect         図郭を自動検出する（デフォルト: True）
  --no-auto-detect      図郭を自動検出しない
```

### 出力ファイル

1. **GCPファイル** (JSON形式)：
   - 画像の四隅のピクセル座標と対応する緯度経度情報を含む
   - デフォルトのファイル名は `<画像名>_gcp.json`

2. **デモ画像** (JPEG形式)：
   - 元の画像に図郭と制御点を可視化したもの
   - デフォルトのファイル名は `<画像名>_demo.jpg`

### 使用例

```bash
# 基本的な使用例
gaihozu process map.jpg --ul 35.123,139.456 --ur 35.123,139.789 --ll 34.987,139.456 --lr 34.987,139.789

# 出力ファイルを指定
gaihozu process map.jpg --ul 35.123,139.456 --ur 35.123,139.789 --ll 34.987,139.456 --lr 34.987,139.789 --gcp-output gcp.json --demo-output demo.jpg

# 図郭の自動検出を無効化
gaihozu process map.jpg --ul 35.123,139.456 --ur 35.123,139.789 --ll 34.987,139.456 --lr 34.987,139.789 --no-auto-detect
```

## 開発

### テストの実行

```bash
# すべてのテストを実行
poetry run pytest

# カバレッジレポートを生成
poetry run pytest --cov=gaihozu
```

### コードフォーマット

```bash
# Blackでコードをフォーマット
poetry run black gaihozu tests

# isortでインポートをソート
poetry run isort gaihozu tests
```

### 型チェック

```bash
# mypyで型チェック
poetry run mypy gaihozu
```

## プロジェクト構造

```
gaihozu-georecognition/
├── pyproject.toml        # Poetry設定ファイル
├── README.md             # このファイル
├── LICENSE               # MITライセンス
├── gaihozu/              # メインパッケージ
│   ├── __init__.py       # バージョン情報
│   ├── cli.py            # CLIインターフェース
│   ├── image_processor.py # 画像処理機能
│   ├── gcp_generator.py  # GCP生成機能
│   └── visualizer.py     # 可視化機能
└── tests/                # テスト
    ├── __init__.py
    ├── test_image_processor.py
    ├── test_gcp_generator.py
    ├── test_visualizer.py
    └── test_cli.py
```

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

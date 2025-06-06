# gaihozu-georecognition 詳細仕様

このドキュメントでは、gaihozu-georecognitionの技術的な詳細仕様について説明します。

## パラメータ詳細説明

### Binary Threshold (二値画像変換の閾値)
- **範囲**: 1-255
- **デフォルト**: 100
- **説明**: グレースケール画像を二値画像に変換する際の閾値。値が小さいほど多くの領域が白になります。

### Erode Kernel (erodeのkernelの大きさ)
- **範囲**: 1-10
- **デフォルト**: 3
- **説明**: モルフォロジー演算（erode）で使用するカーネルのサイズ。細い線の除去に影響します。

### Erode Iteration (erodeの実行回数)
- **範囲**: 1-10
- **デフォルト**: 2
- **説明**: erode処理を繰り返す回数。多いほど細い線がより除去されます。

### Line Accumulation (直線認識の閾値)
- **範囲**: 1000-50000
- **デフォルト**: 10000
- **説明**: Hough変換で直線として認識するために必要な投票数。値が大きいほど長い直線のみが検出されます。

### Rho Precision (ρの精度)
- **範囲**: 1-10
- **デフォルト**: 2
- **説明**: Hough変換における距離パラメータの精度（ピクセル単位）。

### Theta Precision (θの精度)
- **範囲**: 1-180
- **デフォルト**: 2
- **説明**: Hough変換における角度パラメータの精度。値はπ/値で計算されます。

### オフセット（0 - 100%）
- **範囲**: 0-100
- **デフォルト**: 0
- **説明**: グループ化された線を内側にオフセットさせる割合。地図の図郭と真の4隅の間にあるマージンを調整するために使用します。線の向き（縦/横）を自動判定し、適切な方向にオフセットします。

## 直線グループ化機能

検出された直線は以下の基準で自動的にグループ化されます：

- **距離の類似性**: rho（距離）の差が500ピクセル以内
- **角度の類似性**: theta（角度）の差がπ/18ラジアン以内

類似した直線は同じグループに分類され、グループごとに異なる色で表示されます。

## オフセット機能について

地図の図郭（外枠）を検出する際、検出される線と地図の真の4隅の間にはマージンが存在することがあります。オフセット機能を使用して調整することができます。

オフセット機能は以下のように動作します：

1. **線の向き判定**: 検出された線の角度（theta）から、その線が縦向きか横向きかを自動判定
   - theta < π/4 または theta > 3π/4 の場合：縦向き
   - それ以外の場合：横向き

2. **オフセット方向の決定**: 線の向きと画像の中心からの位置に基づいて、内側へのオフセット方向を決定
   - 縦線：画像の中心より右側の線は左に、左側の線は右にオフセット
   - 横線：画像の中心より下側の線は上に、上側の線は下にオフセット

3. **オフセット量の計算**: 画像サイズに対する相対的な割合（0-100%）で指定
   - 最大オフセット量は画像の短辺の30%まで
   - 実際のオフセット量 = 最大オフセット量 × (設定値 / 100)

スキャン状況によって異なりますが、外邦図の場合は、5.6%程度を指定すると多くの画像に当てはまりうまくいくようです。

## プロファイル管理機能詳細

パラメータ設定を保存・管理する機能により、効率的な作業が可能です。

### 機能概要

- **パラメータ保存**: 現在の7つのパラメータ設定を名前付きで保存
- **プロファイル一覧**: 保存されたプロファイルをリスト表示
- **設定復元**: 保存されたプロファイルをクリックして設定を復元
- **プロファイル削除**: 不要なプロファイルをチェックボックスで選択して削除
- **現在のプロファイル表示**: 適用中のプロファイル名を表示

### 使用方法

#### プロファイルの保存
1. パラメータスライダーで最適な設定を調整
2. 「現在の設定を保存」ボタンをクリック
3. プロンプトでプロファイル名を入力
4. プロファイルがリストに追加され、保存日時と共に表示

#### プロファイルの適用
1. プロファイルリストから適用したいプロファイルをクリック
2. 全パラメータが自動的に復元される
3. 「現在のプロファイル」表示が更新される
4. 選択されたプロファイルがハイライト表示される

#### プロファイルの削除
1. 削除したいプロファイルのチェックボックスを選択（複数選択可能）
2. 「選択したプロファイルを削除」ボタンをクリック
3. 確認ダイアログで削除対象を確認
4. 「OK」で削除実行

### データ保存

- **保存場所**: ブラウザのローカルストレージ
- **保存内容**: プロファイル名、保存日時、7つのパラメータ値
- **永続性**: ブラウザデータを削除するまで保持
- **共有**: 同一ブラウザ・同一ドメインでのみ利用可能

### プロファイルデータ構造

```json
{
  "profiles": [
    {
      "id": "1640995200000",
      "name": "高精度設定",
      "timestamp": "2024/1/1 12:00:00",
      "parameters": {
        "binary_threshold": 120,
        "erode_kernel": 2,
        "erode_iteration": 1,
        "line_accumulation": 15000,
        "rho_precision": 1,
        "theta_precision": 1.5708,
        "line_offset": 10
      }
    }
  ]
}
```

### 注意事項

- パラメータを手動で変更すると、現在のプロファイル名が「デフォルト」にリセットされます
- ブラウザのプライベートモードでは、セッション終了時にデータが削除されます
- ブラウザの設定でローカルストレージが無効化されている場合、機能が利用できません

## バッチ処理機能詳細

複数の地図画像に対して一括で交点計算を実行し、結果をCSVファイルとして出力する機能です。大量の地図データを効率的に処理できます。

### 機能概要

- **一括処理**: 指定したディレクトリ内のすべての画像を自動処理
- **現在のパラメータ適用**: 調整済みのパラメータ設定をすべての画像に適用
- **CSV出力**: 処理結果を構造化されたCSVファイルとして保存
- **エラーハンドリング**: 処理に失敗した画像についても詳細なエラー情報を記録
- **プレビュー機能**: 処理結果をブラウザ上で即座に確認可能

### 使用方法

#### 基本的な処理手順
1. **パラメータ調整**: 単一画像で最適なパラメータを調整
2. **バッチ処理実行**: 「すべての画像の交点を計算」ボタンをクリック
3. **処理完了待機**: 画像数に応じて数秒〜数分の処理時間
4. **結果確認**: 処理完了後、成功・失敗の統計情報を表示
5. **CSV取得**: ダウンロードリンクまたはプレビュー機能で結果を確認

#### 処理対象画像
- **対象ディレクトリ**: 起動時に指定したディレクトリ（デフォルト: `targets/`フォルダ）
- **対応形式**: .jpg, .jpeg, .png
- **処理順序**: ファイル名のアルファベット順
- **自動検出**: フォルダ内の対応形式ファイルを自動的に検出

### CSV出力フォーマット

#### ヘッダー構成
```csv
画像ファイル名,x0,y0,x1,y1,x2,y2,x3,y3,error
```

#### データ構造
- **画像ファイル名**: 処理対象の画像ファイル名
- **x0,y0**: 左上の交点座標
- **x1,y1**: 右上の交点座標
- **x2,y2**: 左下の交点座標
- **x3,y3**: 右下の交点座標
- **error**: エラーメッセージ（成功時は空白）

#### 成功例
```csv
画像ファイル名,x0,y0,x1,y1,x2,y2,x3,y3,error
map001.jpg,120,150,980,145,125,850,975,855,
map002.jpg,110,140,990,138,115,860,985,865,
```

#### エラー例
```csv
画像ファイル名,x0,y0,x1,y1,x2,y2,x3,y3,error
map003.jpg,,,,,,,,,線が検出されませんでした
map004.jpg,,,,,,,,,交点が4つではありません（2個）
map005.jpg,,,,,,,,,グループ数が多すぎます（15個）
```

### エラーハンドリング

処理中に発生する可能性のあるエラーとその対処法：

#### 1. 画像読み込みエラー
- **原因**: ファイルが破損している、対応していない形式
- **メッセージ**: "画像の読み込みに失敗しました"
- **対処法**: 画像ファイルの形式・整合性を確認

#### 2. 線検出エラー
- **原因**: パラメータが適切でない、画像に直線が含まれていない
- **メッセージ**: "線が検出されませんでした"
- **対処法**: パラメータ調整、特に`line_accumulation`を下げる

#### 3. グループ数エラー
- **原因**: 検出された直線が多すぎる（10グループ超過）
- **メッセージ**: "グループ数が多すぎます（N個）"
- **対処法**: `line_accumulation`を上げて検出線数を減らす

#### 4. 交点数エラー
- **原因**: 4つの交点が検出されない
- **メッセージ**: "交点が4つではありません（N個）"
- **対処法**: パラメータ調整で適切な4本の直線を検出させる

#### 5. 交点並べ替えエラー
- **原因**: 交点の位置関係が想定と異なる
- **メッセージ**: "交点の並べ替えに失敗しました"
- **対処法**: オフセット値の調整

### 処理性能

- **処理速度**: 1画像あたり約1-3秒（画像サイズ・パラメータに依存）
- **メモリ使用量**: 画像サイズに比例（通常数十MB程度）
- **同時処理**: 順次処理（並列処理なし）
- **進捗表示**: 処理中インジケータで進捗を表示

## CSVプレビュー機能詳細

バッチ処理完了後、CSVファイルの内容をブラウザ上で即座に確認できる機能です。

### 機能概要

- **即座にプレビュー**: ダウンロードせずにブラウザ上で結果確認
- **テーブル表示**: 見やすい表形式でデータを表示
- **色分け表示**: 成功・失敗を視覚的に区別
- **スクロール対応**: 大量データでも快適に閲覧
- **制限表示**: 最大100行まで表示（パフォーマンス考慮）

### 表示仕様

#### ヘッダー情報
- **総行数**: 処理された画像の総数
- **表示行数**: プレビューで表示している行数
- **制限表示**: 100行を超える場合は制限表示の旨を明記

#### 視覚的表現
- **成功行**: 緑色のテキストで「成功」と表示
- **エラー行**: 赤色の背景でエラーメッセージを表示
- **ホバー効果**: 行にマウスオーバーで背景色変更
- **固定ヘッダー**: スクロール時もヘッダーが固定表示

#### テーブル構造


画像ファイル名|x0|y0|x1|y1|x2|y2|x3|y3|error    
--|--|--|--|--|--|--|--|--|--
map001.jpg|120 |150 |980 |145 |125 |850 |975 |855 | 成功     
map002.jpg|110 |140 |990 |138 |115 |860 |985 |865 | 成功     
map003.jpg|    |    |    |    |    |    |    |    | 線が検出…


### 使用方法

1. **バッチ処理実行**: 「すべての画像の交点を計算」ボタンをクリック
2. **処理完了待機**: 処理完了まで待機
3. **プレビューボタン**: 「CSVプレビュー」ボタンをクリック
4. **結果確認**: テーブル形式で結果を確認
5. **詳細分析**: 成功・失敗の分布を視覚的に把握

## プロジェクト構成

```
gaihozu-georecognition/
├── app.py                 # Flaskサーバーのメインファイル
├── index.html            # Webインターフェース
├── line_detector.py      # 直線検出関数
├── requirements.txt      # 依存関係
├── targets/             # サンプル画像ディレクトリ
│   ├── *.jpg           # 地図画像ファイル(サンプル)
└── README.md           # ユーザーマニュアル
└── SPEC.md             # 詳細仕様（このファイル）
```

### 主要ファイルの説明

#### app.py
- Flaskベースのバックエンドサーバー
- 画像処理API（`/api/process`）
- 画像リスト取得API（`/api/images`）
- 直線グループ化機能

#### index.html
- レスポンシブWebインターフェース
- パラメータ調整用スライダー
- 結果表示機能
- リアルタイム値更新

#### line_detector.py
- `detect_lines`関数の実装
- OpenCV を使用した Hough 変換による直線検出

## APIエンドポイント

### GET /api/images
サンプル画像のリストを取得

**レスポンス例:**
```json
{
  "images": ["image1.jpg", "image2.jpg", ...]
}
```

### POST /api/process
画像処理を実行

**リクエスト例:**
```json
{
  "image_name": "sample.jpg",
  "parameters": {
    "binary_threshold": 100,
    "erode_kernel": 3,
    "erode_iteration": 2,
    "line_accumulation": 10000,
    "rho_precision": 2,
    "theta_precision": 0.034906585
  }
}
```

**レスポンス例:**
```json
{
  "success": true,
  "image": "data:image/jpeg;base64,/9j/4AAQ...",
  "lines_count": 15,
  "groups_count": 4
}
```

### POST /api/process-all
すべての画像の交点を一括計算

**リクエスト例:**
```json
{
  "parameters": {
    "binary_threshold": 100,
    "erode_kernel": 3,
    "erode_iteration": 2,
    "line_accumulation": 10000,
    "rho_precision": 2,
    "theta_precision": 0.034906585,
    "line_offset": 0
  }
}
```

**レスポンス例:**
```json
{
  "success": true,
  "message": "全5個の画像を処理し、3個の交点を計算しました。CSVファイルに保存しました。",
  "csv_path": "intersections.csv"
}
```

### GET /api/csv-preview
CSVファイルのプレビューを取得

**レスポンス例:**
```json
{
  "success": true,
  "headers": ["画像ファイル名", "x0", "y0", "x1", "y1", "x2", "y2", "x3", "y3", "error"],
  "data": [
    ["map001.jpg", "120", "150", "980", "145", "125", "850", "975", "855", ""],
    ["map002.jpg", "", "", "", "", "", "", "", "", "線が検出されませんでした"]
  ],
  "total_rows": 5,
  "preview_rows": 2
}
```

## 開発・カスタマイズ

### 新しい画像の追加
指定したディレクトリ（デフォルト: `targets/`）に画像ファイル（.jpg, .jpeg, .png）を追加するだけで、自動的にドロップダウンメニューに表示されます。

### パラメータ範囲の変更
`index.html`のスライダー設定を変更することで、パラメータの範囲を調整できます。

### グループ化アルゴリズムの調整
`app.py`の`group_similar_lines`関数内の閾値（500ピクセル、π/18ラジアン）を変更することで、グループ化の感度を調整できます。

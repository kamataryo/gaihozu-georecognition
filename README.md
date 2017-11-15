# gaihozu-georecognition

## 依存ライブラリのインストール

```shell
$ pip install requests
```

## 使い方

`main.py`を使って外邦図1枚をインポートする。他のスクリプトは `main.py`によって自動的に呼び出される。

引数は、地図名 MapWarperのトップページのURL -u ユーザーのメールアドレス -p パスワード

例：

```shell
$ cd 作業ディレクトリ
$ python main.py /home/hogeo/workingdirectory/gomanbunnoichichikeizu343.jpg http://example.com -u user@example.com -p password -c ./attributes.csv 
```

- 作業ディレクトリには、読み込む地図と `attributes.csv`という名前のcsvファイルを前もって置いておく必要あり。 `attributes.csv`の形式については[attributes.csv](./attributes.csv)そのものを参照。
- このCSVから地図のメタデータを取得する。ヘッダーの各項目はMap Warper APIにおける地図のattributesの項目と一致しなければならない。ただし足りない項目があるのはかまわない。
- ヘッダーに対応する値がない時は空の値を入れておく。
- `main.py`の引数に入力する地図名と、 `attributes.csv`の `unique_id` または `title`の項目の少なくとも1つは、一字一句違わず一致しなければならない。
- メタデータの値のうち `date_depicted`と `issue_year`はAPIの仕様により4文字まで。

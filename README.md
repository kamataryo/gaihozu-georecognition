# gaihozu-georecognition

main.pyを使って外邦図1枚をインポートする。
他のスクリプトはmain.pyによって自動的に呼び出される。
引数は、地図名 MapWarperのトップページのURL -u ユーザーのメールアドレス -p パスワード<br>
例：<br><br>

$ cd 作業ディレクトリ<br>
$ python import.py gomanbunnoichichikeizu343.jpg http://ec2-52-198-241-210.ap-northeast-1.compute.amazonaws.com:8080 -u super@example.com -p your_password
<br><br>

作業ディレクトリには、読み込む地図と"attributes.csv"という名前のcsvファイルを前もって置いておく必要あり。
attributes.csvの形式についてはattributes.csvそのものを参照。
このCSVから地図のメタデータが取得される。
ヘッダーの各項目はMap Warper APIにおける地図のattributesの項目と一致しなければならない。
ただし足りない項目があるのはかまわない。
ヘッダーに対応する値がない時は空の値を入れておく。
main.pyの引数に入力する地図名と、attributes.csvの"unique_id"または"title"の項目の少なくとも1つは、一字一句違わず一致しなければならない。
メタデータの値のうち"date_depicted"と"issue_year"はAPIの仕様により4文字まで。

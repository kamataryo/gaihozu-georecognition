# gaihozu-georecognition

main.pyを使ってインポート外邦図1枚をインポートする。
他のスクリプトはmain.pyによって自動的に呼び出される。
引数は、地図名、Map WarperのトップページのURL、 -u ユーザーのメールアドレス -p パスワード
例。

$ cd 作業ディレクトリ
$ python import.py gomanbunnoichichikeizu343.jpg http://ec2-52-198-241-210.ap-northeast-1.compute.amazonaws.com:8080 -u super@example.com -p your_password

作業ディレクトリに前もって読み込む地図と"attributes.csv"という名前のcsvファイルを置いておく必要あり。

attributes.csvの形式についてはattributes.csvそのものを参照。
headerの項目はいじらないこと。
headerに対応する値が地図にない時は空の値を入れておく。
import.pyの引数として入力する地図名と、attributes.csvのunique_idまたはtitleの項目の少なくとも1つは、一字一句違わず一致しなければならない。
date_depictedとissue_yearはAPIの仕様により4文字まで。

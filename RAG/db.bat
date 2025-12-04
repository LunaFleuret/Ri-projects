@echo off
REM バッチファイルがあるフォルダに移動（重要）
cd d %~dp0

echo 薫衣りぃ配信検索アプリを起動しています...
echo ブラウザが自動的に開きます。
echo ※この黒い画面は閉じないでください！閉じるとアプリが終了します。

REM アプリを起動
py -m streamlit run app.py

REM 何かエラーがあった時に画面がすぐ消えないようにする
pause
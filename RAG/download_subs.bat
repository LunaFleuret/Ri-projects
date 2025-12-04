@echo off
chcp 65001 > nul
echo ========================================================
echo  薫衣りぃ RAG 字幕ダウンローダー
echo ========================================================
echo.
echo YouTubeのURLを入力すると、字幕をダウンロードして
echo データベースを自動更新します。
echo.

python download_subs.py

echo.
echo 処理が完了しました。何かキーを押すと終了します。
pause > nul

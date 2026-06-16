WC Simulator 配布用メモ

配布するもの:
- WC_Simulator.exe
- README.txt

起動方法:
1. zipを展開します。
2. WC_Simulator.exeをダブルクリックします。
3. 初回起動時に、同じフォルダへ developer.db と user_db フォルダが自動作成されます。

注意:
- zipのまま実行せず、必ず展開してから実行してください。
- Program Files など書き込み権限が必要な場所ではなく、デスクトップやドキュメントなどの通常フォルダに置いてください。
- developer.db と user_db はユーザー情報やシミュレーション結果を保存するため、利用開始後は削除しないでください。
- 初期状態に戻したい場合は、アプリを閉じてから developer.db と user_db を削除してください。次回起動時に初期DBが再作成されます。

管理者向け:
- 既存ユーザーDBを削除し developer.db を作り直す場合は、ソースフォルダで次を実行します。
  python reset.py --target dist
- その後、PyInstallerで再ビルドして配布zipを作成してください。

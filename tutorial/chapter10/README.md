[Chapter10] ログイン機能作成
--
[top](../../README.md)

# Note

このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter10/src` をルートディレクトリとして解説します。

# ■ アプリの起動

Nuxtサーバーは run.sh からも起動可能なので、APIサーバーと合わせて起動してみましょう

```bash
# ※ 起動していない場合のみ
./bin/mysql.sh

# 開発用shellを起動
./bin/run.sh chapter10 --mode shell

# データベースの初期化
./bin/init-database.sh

exit

# APIサーバーとNuxtサーバーを起動
./bin/run.sh chapter10 --mode app
```

ブラウザから NuxtサーバーとAPIサーバーにアクセスしてみましょう。

- Nuxtサーバー: http://localhost:3000/
- APIサーバー: http://localhost:8018/docs
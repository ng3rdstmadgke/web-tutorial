[Chapter11] アイテム管理ページ(CRUD)の実装
--
[top](../../README.md)

# Note

このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter11/src` をルートディレクトリとして解説します。

chapter10では、アイテム管理ページを実装します。

# ■ アプリの起動

Nuxtサーバーは run.sh からも起動可能なので、APIサーバーと合わせて起動してみましょう

```bash
# ※ 起動していない場合のみ
./bin/mysql.sh

# 開発用shellを起動
./bin/run.sh chapter11 --mode shell

# データベースの初期化
./bin/init-database.sh

exit

# APIサーバーとNuxtサーバーを起動
./bin/run.sh chapter11 --mode app
```

ブラウザから NuxtサーバーとAPIサーバーにアクセスしてみましょう。

- Nuxtサーバー: http://localhost:3000/
- APIサーバー: http://localhost:8018/docs

```bash
# 開発用shellを起動
./bin/run.sh chapter11 --mode shell

# ディレクトリ作成
cd front
mkdir -p assets components composables layouts middleware modules pages plugins utils
```

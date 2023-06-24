[Chapter8] 番外編2: TypeScriptのおさらい
--
[top](../../README.md)

# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter8/src` をルートディレクトリとして解説します。

Chapter8では、TypeScriptに触れていきましょう。  
最終的にフロントエンドはNuxt.jsを利用して実装する予定ですが、そもそもTypeScriptに触れたことがないと説明が難しいのでここで簡単に説明したいと思います。


# ■ アプリを起動しましょう

```bash
# データベースの起動
./bin/mysql.sh

# 開発用shellを起動
./bin/run.sh chapter8 --mode shell

# DBの初期化
./bin/init-database.sh

exit
```

アプリの起動

```bash
./bin/run.sh chapter8 --mode app
```

[Chapter7] 番外編1: JavaScriptに触れてみよう。
--
[top](../../README.md)

# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter7/src` をルートディレクトリとして解説します。

Chapter7では、JavaScriptに触れていきましょう。  
最終的にフロントエンドはNuxt.jsを利用して実装する予定ですが、そもそもJavaScriptに触れたことがないと説明が難しいのでここで簡単に説明したいと思います。


# ■ アプリを起動しましょう

```bash
# データベースの起動
./bin/mysql.sh

# 開発用shellを起動
./bin/run.sh chapter7 --mode shell

# DBの初期化
./bin/init-database.sh

exit
```

アプリの起動

```bash
./bin/run.sh chapter7
```


# ■ FastAPIで静的ファイルをレスポンスできるようにする

JavaScriptはブラウザで動作する言語です。FastAPIからhtml, css, jsなどの静的ファイルをレスポンスできるようにしましょう。  
`/opt/app/static` 配下の静的ファイルをレスポンスするルートを登録してみましょう。

```python
# --- main.py ---
from fastapi import FastAPI
from routers import router
from fastapi.staticfiles import StaticFiles  # 追加

app = FastAPI()

app.include_router(router, prefix="/api/v1")

# html=True : パスの末尾が "/" の時に自動的に index.html をロードする
# name="static" : FastAPIが内部的に利用する名前を付けます
app.mount("/", StaticFiles(directory=f"/opt/app/static", html=True), name="static")  # 追加
```

htmlを作成します。

```html
<!-- static/index.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<body>
<h1>Hello World!!</h1>
</body>
</html>
```

ブラウザからアクセスしてみましょう
http://localhost:8018/


# ■ JavaScriptの文法

## 変数定義

```js
```

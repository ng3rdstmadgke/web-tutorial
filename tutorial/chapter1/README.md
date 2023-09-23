[Chapter1] FastAPI入門
--
[top](../../README.md)

# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter1/src` をルートディレクトリとして解説します。

# FastAPIに触れてみましょう

まずはサンプルのアプリを起動して、FastAPIを動かしてみましょう

```bash
# FastAPIを起動
./bin/run.sh chapter1 --mode app --sample
```

http://127.0.0.1:8018/docs にブラウザでアクセスしてみましょう。


# 簡単なAPIを実装してみましょう

`/` にアクセスすると `{"Hello": "World"}` をレスポンスるするAPIです。  
FastAPIでは、FastAPIインスタンスにルートを登録していくイメージでAPIを実装していきます。

```python
# -- api/main.py --

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

それではアプリを起動してみましょう。  
<font color="red">※ 一旦サンプルアプリを落としてください</font>

```bash
./bin/run.sh chapter1 --mode app
```

http://127.0.0.1:8018/ にブラウザでアクセスして、動作を確認してみましょう。


次に、URLにプレースホルダ( `item_id` )が設定されていて、GETパラメータ ( `q` )を受け取るAPIを定義してみましょう。

```python
# -- api/main.py --

# ... 略 ...

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = ""):
    return {"item_id": item_id, "q": q}
```

http://127.0.0.1:8018/items/1?q=hogehoge にブラウザでアクセスして、動作を確認してみましょう。
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

- http://127.0.0.1:8018/docs
ブラウザでアクセスして、APIの動作を確かめてみましょう


# 簡単なAPIを実装してみましょう

まずは `/users/{user_id}` という簡単なAPIを実装してみましょう。
FastAPIでは、FastAPIインスタンス( `app` ) にURLとそのURLにアクセスしたときに実行される関数を登録していきます。  
このAPIはURLにプレースホルダ( `item_id` )が設定されていて、GETパラメータ ( `query` )を受け取ります。  

```python
# -- api/main.py --

from fastapi import FastAPI, Request, Response, HTTPException

app = FastAPI()

@app.get("/users/{user_id}")
def sample(
    user_id: int,  # パスパラメータ
    query: str = ""    # クエリパラメータ
):
    # パスパラメータ、クエリパラメータで受け取った値を返す
    return {"user_id": user_id, "query": query}
```

それではアプリを起動してみましょう。  

```bash
./bin/run.sh chapter1 --mode app
```

- http://127.0.0.1:8018/docs  
ブラウザでアクセスして動作を確かめてみましょう。
- http://127.0.0.1:8018/users/1?q=hogehoge  
直接アクセスして動作を確かめてみましょう。


# レガシーなwebアプリの実装

※ すでにWeb開発の経験がある方は飛ばしてください

さて、先程簡単なAPIを実装してみたわけですが、あまりピンとこない方もいるのではないでしょうか。  
様々なWebフレームワークが流行っては廃れを繰り返す中で、Webフレームワークはなるべく簡単に短い記述で実装できるように改良されてきました。  
そのため、初めてWebフレームワークに触れ方の中には「これだけ?」「なんか動いているけど正直良くわからない、、、」というような感想を抱いてしまう方もいるのではないでしょうか。
そこで、この章ではあえて昔ながらのwebアプリを実装することで、webの仕組を理解し、その問題点にフォーカスしていきましょう。

## RequestとResponseを確認する

まず、HTTPリクエストとHTTPレスポンスの扱いを見てみましょう。  
一般的にFastAPIにおいて、リクエストオブジェクトとレスポンスオブジェクトを直接利用することはありませんが、リクエストオブジェクト( `Request` )を受け取って、レスポンスオブジェクト( `Response` )を返却するといった実装することは可能です。  

- [リクエストオブジェクト Request](https://www.starlette.io/requests/)  
  HTTPリクエストを表すオブジェクト。  
  `Request` はHTTPリクエストの情報をまとめたオブジェクトで、 URLやHTTPメソッド、リクエストヘッダ、リクエストボディなどが含まれています。
- [レスポンスオブジェクト Response](https://www.starlette.io/responses/)  
  HTTPレスポンスとなるオブジェクト。  
  `Response` はFastAPIによってHTTPレスポンスに変換されるオブジェクトで、レスポンスボディ、レスポンスヘッダ、ステータスコードを指定します。

GET, POSTメソッドで受け取ったリクエストをそのままjson形式でレスポンスするAPIを実装します。

```python
# -- api/main.py --

# --- --- --- 略 --- --- ---

import json

# GETメソッド
@app.get("/info/{id}", tags=["Info"])
async def info_get(request: Request):
    body = {
        "url": str(request.url),
        "method": request.method,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "path_params": dict(request.path_params),
        "client": request.client,
        "cookie": dict(request.cookies),
        "body": (await request.body()).decode("utf-8"),
    }
    print(body)
    return Response(
        content=json.dumps(body, ensure_ascii=False),
        status_code=200,
        headers={
            "Content-Type": "application/json",
        },
    )
```

動作確認

- http://127.0.0.1:8018/info/1  
リクエスト情報が表示してみましょう。  
- http://127.0.0.1:8018/info/1?foo=bar&hoge=fuga  
クエリパラメータを付与すると、 `query_params` に付与したクエリパラメータが表示されます。  


```python
# -- api/main.py --

# --- --- --- 略 --- --- ---

# POSTメソッド
@app.post("/info/{id}", tags=["Info"])
async def info_post(request: Request):
    body = {
        "url": str(request.url),
        "method": request.method,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "path_params": dict(request.path_params),
        "client": request.client,
        "cookie": dict(request.cookies),
        "body": (await request.body()).decode("utf-8"),
    }
    print(body)
    return Response(
        content=json.dumps(body, ensure_ascii=False),
        status_code=200,
        headers={
            "Content-Type": "application/json",
        },
    )

```

動作確認

`curl` でAPIにアクセスしてみましょう。

```bash
curl -s -X 'POST' \
   'http://127.0.0.1:8018/info/100' \
   -H 'accept: application/json' \
   -d '{"foo": "bar", "hoge": "fuga"}' | jq .
```

## 実装

さて、 `Request` `Response` オブジェクトの動作が大体把握できたところで、昔ながらのwebアプリを実装してみましょう。  

### アイテム一覧

グローバルに定義した `ITEMS` をリスト表示するHTMLを返却するページを実装します。  
クエリパラメータ `search` でアイテム名の中間一致検索。ができるようにしておきます。  

```python
# -- api/main.py --

# --- --- --- 略 --- --- ---

from fastapi.responses import RedirectResponse

ITEMS = {
    1: {"id": 1, "name": "Apple" , "price": 100},
    2: {"id": 2, "name": "Banana", "price": 200},
    3: {"id": 3, "name": "Orange", "price": 150},
}

@app.get("/items/", tags=["Legacy"])
async def read_items_get(request: Request):
    search = request.query_params.get("search", None)
    rows = []
    for id, e in ITEMS.items():
        if search and (search not in e["name"].lower()):
            # searchパラメータが指定されていてかつ、nameと中間一致しなければスキップ
            continue

        row = f"""
            <tr>
              <th scope="row"><a href="/items/{id}">{id}</a></th>
              <td>{e["name"]}</td>
              <td>{e["price"]}</td>
            </tr>
        """
        rows.append(row)
    html = f"""
    <DOCTYPE html>
    <html>
      <head>
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" crossorigin="anonymous">
      </head>
      <body class="container">
        <p class="fs-1"><a href="/items/">App</a></p>
        <a class="btn btn-primary" href="/items/create/" role="button">Create</a>
        <table class="table table-striped">
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Name</th>
              <th scope="col">Price</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
    </html>
    """
    return Response(
        content=html,
        status_code=200,
        headers={ "Content-Type": "text/html; charset=UTF-8" },
    )

```

動作確認

- http://127.0.0.1:8018/items/  
アイテムの一覧が表示してみましょう。  
- http://127.0.0.1:8018/items/?search=app  
クエリパラメータに `search=app` を指定するとApple。のみ表示されます。  


### アイテム詳細

パスパラメータ `item_id` で指定されたidを持つアイテムを表示するHTMLを返却します。  
指定されたIDが存在しない場合は `404 Not Found` を。返却します。  


```python
# -- api/main.py --

# --- --- --- 略 --- --- ---

@app.get("/items/{item_id}", tags=["Legacy"])
async def read_item_get(request: Request):
    # パスからitem_idを取得
    item_id = int(str(request.path_params.get("item_id")))
    if item_id not in ITEMS:
        # アイテムが存在しなければエラー
        return Response(
            content=f"<h1>ID={item_id} Not Found</h1>",
            status_code=404,
            headers={ "Content-Type": "text/html; charset=UTF-8" },
        )
    html = f"""
    <DOCTYPE html>
    <html>
      <head>
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" crossorigin="anonymous">
      </head>
      <body class="container">
        <p class="fs-1"><a href="/items/">App</a></p>
        <form action="/items/{item_id}/delete/" method="post">
            <button type="submit" class="btn btn-danger">Delete</button>
        </form>
        <ul class="list-group">
          <li class="list-group-item">ID: {item_id}</li>
          <li class="list-group-item">Name: {ITEMS[item_id]["name"]}</li>
          <li class="list-group-item">Price: {ITEMS[item_id]["price"]}</li>
        </ul>
    </html>
    """
    return Response(
        content=html,
        status_code=200,
        headers={ "Content-Type": "text/html; charset=UTF-8" },
    )

```


動作確認

- http://127.0.0.1:8018/items/1  
`id=1` のアイテムの詳細画面が表示してみましょう。  
- http://127.0.0.1:8018/items/100  
存在しないIDを指定すると404エラーになります  


### アイテム新規作成

アイテムの作成には2つのAPIが必要です。  

1. 登録フォームのHTMLを返却するAPI (GETメソッド)  
登録フォームのHTMLを返却します。  
1. 登録フォームを送信したときにアイテムを保存するAPI (POSTメソッド)  
リクエストボディからフォームで指定された `id` `name` `price` を取り出し新しい要素として `ITEMS` に登録します。  
登録が成功したら、登録したアイテムの詳細ページにリダイレクトし、重複したIDが存在する場合は `400 Bad Request` を返却します。  


```python
# -- api/main.py --

# --- --- --- 略 --- --- ---


# 登録フォームのHTMLを返却するAPI
@app.get("/items/create/", tags=["Legacy"])
async def create_item_get(request: Request):
    # パスからitem_idを取得
    html = f"""
    <DOCTYPE html>
    <html>
      <head>
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" crossorigin="anonymous">
      </head>
      <body class="container">
        <p class="fs-1"><a href="/items/">App</a></p>
        <form action="/items/create/" method="post">
            <div class="mb-3">
              <label for="id" class="form-label">ID</label>
              <input type="number" name="id" class="form-control" id="id" required>
            </div>
            <div class="mb-3">
              <label for="name" class="form-label">Name</label>
              <input type="text" name="name" class="form-control" id="name" required>
            </div>
            <div class="mb-3">
              <label for="price" class="form-label">Price</label>
              <input type="number" name="price" class="form-control" id="price" required>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </html>
    """
    return Response(
        content=html,
        status_code=200,
        headers={ "Content-Type": "text/html; charset=UTF-8" },
    )


# 登録フォームを送信したときに送信したときに実行されるAPI
@app.post("/items/create/", tags=["Legacy"])
async def create_item_post(request: Request):
    # formで入力された情報を取り出す
    form = await request.form()
    id = int(str(form["id"]))
    name = str(form["name"])
    price = int(str(form["price"]))
    if id in ITEMS:
        # 指定したidがすでに存在していたらエラー
        return Response(
            content=f"<h1>ID={id} Already Exists</h1>",
            status_code=400,
            headers={ "Content-Type": "text/html; charset=UTF-8" },
        )
    ITEMS[id] = { "id": id, "name": name, "price": price }
    # アイテム詳細ページにリダイレクト
    return RedirectResponse(url=f"/items/{id}", status_code=302)

```

動作確認

- http://127.0.0.1:8018/items/create/  
アイテムの登録フォームにアクセスして、アイテムを登録してみましょう。  

### アイテム削除

アイテム詳細ページの `Delete` ボタンがクリックされたときに実行され、パスパラメータに指定されたIDのアイテムを削除します。  

削除が成功したら、アイテム一覧ページにリダイレクトし、指定したIDが `ITEMS` に存在しない場合は `404 Not Found` を返却します。  


```python
# -- api/main.py --

# --- --- --- 略 --- --- ---


@app.post("/items/{item_id}/delete/", tags=["Legacy"])
async def delete_item_post(request: Request):
    item_id = int(str(request.path_params.get("item_id")))
    if item_id not in ITEMS:
        # 指定したidが存在しなければエラー
        return Response(
            content=f"<h1>ID={item_id} Not Found</h1>",
            status_code=400,
            headers={ "Content-Type": "text/html; charset=UTF-8" },
        )
    del ITEMS[item_id]
    return RedirectResponse(url="/items/", status_code=302)
```

動作確認

- http://127.0.0.1:8018/items/1  
詳細ページにアクセスして `Delete` ボタンをクリックしてみましょう。

# レガシーなWebアプリは何がダメなのか

さて、これまで昔ながらのWebアプリを実装して来たわけですがいかがでしょう。  
隠蔽されている部分が少なくてわかりやすかったかもしれませんし、冗長に感じたかも知れません。  
ではここから、昔ながらのWebアプリのどこがまずいのかを考えていきましょう。  

ざっくりこのような問題があります。  

1. リクエストで受け取るパラメータとその型が明確ではない
2. レスポンスで返す値とその型が明確ではない
3. 処理とデザインが密結合している

## 1. 受け取るパラメータとその型が明確ではない

アイテムの新規登録API(POST)を見てみましょう。  
このAPIはパッと見必要なパラメータとその型がわかりません。リクエストとして必要なパラメータはRequestオブジェクトに内包され隠蔽されています。  
そうなると、この関数に対する変更が非常に難しくなります。というのもパラメータと型がわからない状況では処理の把握が難しく、テストで考慮しなければならないパターンも膨大になります。  
処理が把握しきれず、テストも不十分となると、リファクタリングや機能追加の際、既存の機能に変更が生じていないかの確認が困難となり、開発すればするほど負債が増える負のスパイラルが発生します。  


```python
@app.post("/items/create/", tags=["Legacy"])
async def create_item_post(request: Request):
    form = await request.form()
    id = int(str(form["id"]))
    name = str(form["name"])
    price = int(str(form["price"]))
    if id in ITEMS:
        return Response(
            content=f"<h1>ID={id} Already Exists</h1>",
            status_code=400,
            headers={ "Content-Type": "text/html; charset=UTF-8" },
        )
    ITEMS[id] = { "id": id, "name": name, "price": price }
    # アイテム詳細ページにリダイレクト
    return RedirectResponse(url=f"/items/{id}", status_code=302)
```

## 2. レスポンスで返す値とその型が明確ではない

アイテム一覧ページのAPIを見てみましょう。  
このAPIはHTMLを返しており、どんな値をHTMLにレンダリングしているのかをテストするのが困難です。  
HTMLをパースして、レンダリングされるべき値が入っていることを確認すればいいでしょうか。かなり面倒ですし、HTML文字列になった時点で型の情報は消失しているため厳密なチェックはできません。  
後述の処理とデザインとの密結合との合せ技で、かなりバグが発生しやすいコードとなります。  


```python
@app.get("/items/", tags=["Legacy"])
async def read_items_get(request: Request):
    search = request.query_params.get("search", None)
    rows = []
    for id, e in ITEMS.items():
        if search and (search not in e["name"].lower()):
            continue

        row = f"""
            <tr>
              <th scope="row"><a href="/items/{id}">{id}</a></th>
              <td>{e["name"]}</td>
              <td>{e["price"]}</td>
            </tr>
        """
        rows.append(row)
    html = f"""
    <DOCTYPE html>
    <html>
      <head>
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" crossorigin="anonymous">
      </head>
      <body class="container">
        <p class="fs-1"><a href="/items/">App</a></p>
        <a class="btn btn-primary" href="/items/create/" role="button">Create</a>
        <table class="table table-striped">
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Name</th>
              <th scope="col">Price</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
    </html>
    """
    return Response(
        content=html,
        status_code=200,
        headers={ "Content-Type": "text/html; charset=UTF-8" },
    )
```

## 3. 処理とデザインが密結合している

HTMLを返却するAPIはどう頑張っても処理とデザインが密結合してしまいます。これには大きく2つの問題があります。  

1. APIの再利用ができない  
似たような処理は共通化したいところですが、処理にデザインがくっついていると再利用できません。  

2. 実装時の考慮事項が増える  
つまり「処理だけを変更したいのにデザインも考慮しなければならない」、もしくは「デザインだけを変更したいのに処理も考慮しなければならない」ということです。  
こうなると、リファクタリングや機能追加の際に考慮事項が増え開発スピードが低下します。加えてテストが困難で意図しないバグも発生しやすくなります。  

# モダンなAPIへ

レガシーなWebアプリのダメな部分を見てきました。  
この章ではFastAPI本来の書き方で再実装して、ダメな部分がどのように改善するのかを見ていきましょう。  

FastAPIではレガシーなwebの問題点を以下のように解決することができます。

1. リクエストのパラメータとその型が明確  
パスパラメータ、クエリパラメータ、リクエストボディで受け取るパラメータを関数の引数として定義可能。  
値が足りない、型が異なる場合はFastAPI側で自動的に `422 Unprocessable Entity` エラーが返却されます。  
2. レスポンスの値とその型が明確  
APIが返却する値とその型をデコレータで指定可能。  
返却された値の型が異なっていた場合は `500 Internal Server Error` エラーが返却されます。  
3. APIとデザインが分離している  
FastAPIでは基本的にレスポンスはjsonで返却し、レンダリングはNuxtJSなどフロントエンド側のフレームワークに任せます。  
処理のみにフォーカスしたテストしやすく、再利用性の高いAPIを実装することができます。  


## 実装

### アイテム一覧

- クエリパラメータの `search` を関数の引数として型付きで定義  
- デコレータの `response_model` でレスポンスの型 `ItemsSchema` を明示  


```python
# -- api/main.py --

# --- --- --- 略 --- --- ---

from pydantic import BaseModel
from typing import Optional

class ItemSchema(BaseModel):
    id: int
    name: str
    price: int

class ItemsSchema(BaseModel):
    items: list[ItemSchema]


@app.get("/api/items/", response_model=ItemsSchema, tags=["Modern"])
async def read_items_api (
    search: Optional[str] = None,
):
    ret = {"items": []}
    for _, e in ITEMS.items():
        if search and (search not in e["name"]):
            continue
        ret["items"].append(e)
    return ret
```

### アイテム詳細

- パスパラメータ `item_id` を関数の引数として型付きで定義
- デコレータの `response_model` でレスポンスの型 `ItemSchema` を明示

```python
# -- api/main.py --

# --- --- --- 略 --- --- ---

@app.get("/api/items/{item_id}", response_model=ItemSchema, tags=["Modern"])
async def read_item_api(
    item_id: int,
):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail=f"ID={item_id} not found")
    return ITEMS[item_id]


```

### アイテム新規作成

- リクエストボディ `body` を関数の引数として型付で定義  
- デコレータの `response_model` でレスポンスの型 `ItemSchema` を明示  

```python
# -- api/main.py --

# --- --- --- 略 --- --- ---

@app.post("/api/items/create/", response_model=ItemSchema, tags=["Modern"])
async def create_item_api(
    body: ItemSchema,
):
    if body.id in ITEMS:
        raise HTTPException(status_code=400, detail=f"ID={body.id} Already Exists")
    item = {"id": body.id, "name": body.name, "price": body.price }
    ITEMS[body.id] = item
    return item

```

### アイテム削除

- リクエストボディ `body` を関数の引数として型付で定義  
- デコレータの `response_model` でレスポンスの型 `ItemSchema` を明示  


```python
# -- api/main.py --

# --- --- --- 略 --- --- ---

@app.delete("/api/items/{item_id}/", tags=["Modern"])
async def delete_item_api(
    item_id: int,
):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail=f"ID={item_id} not found")
    del ITEMS[item_id]
    return {"id": item_id}
```


動作確認

- http://127.0.0.1:8018/docs  
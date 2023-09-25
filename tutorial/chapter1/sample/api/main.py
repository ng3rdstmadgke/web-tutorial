from fastapi import FastAPI, Request, Response, HTTPException

app = FastAPI()
###########################################
# Sample
###########################################
@app.get("/users/{user_id}")
def sample(
    user_id: int,  # パスパラメータ
    q: str = ""    # クエリパラメータ
):
    return {"user_id": user_id, "q": q}


###########################################
# Request, Response オブジェクト
#   - Request: https://www.starlette.io/requests/
#   - Response: https://www.starlette.io/responses/
###########################################
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


###########################################
# Legacyな実装
###########################################
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


@app.get("/items/{item_id}", tags=["Legacy"])
async def read_item_get(request: Request):
    # パスからitem_idを取得
    item_id = int(str(request.path_params.get("item_id")))
    if item_id not in ITEMS:
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

@app.post("/items/{item_id}/delete/", tags=["Legacy"])
async def delete_item_post(request: Request):
    item_id = int(str(request.path_params.get("item_id")))
    if item_id not in ITEMS:
        return Response(
            content=f"<h1>ID={item_id} Not Found</h1>",
            status_code=400,
            headers={ "Content-Type": "text/html; charset=UTF-8" },
        )
    del ITEMS[item_id]
    return RedirectResponse(url="/items/", status_code=302)


###########################################
# モダンな実装
#   - RESTful Web API の設計(Microsoft): https://learn.microsoft.com/ja-jp/azure/architecture/best-practices/api-design
###########################################
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


@app.get("/api/items/{item_id}", response_model=ItemSchema, tags=["Modern"])
async def read_item_api(
    item_id: int,
):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail=f"ID={item_id} not found")
    return ITEMS[item_id]


@app.post("/api/items/create/", response_model=ItemSchema, tags=["Modern"])
async def create_item_api(
    body: ItemSchema,
):
    if body.id in ITEMS:
        raise HTTPException(status_code=400, detail=f"ID={body.id} Already Exists")
    item = {"id": body.id, "name": body.name, "price": body.price }
    ITEMS[body.id] = item
    return item

@app.delete("/api/items/{item_id}/", tags=["Modern"])
async def delete_item_api(
    item_id: int,
):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail=f"ID={item_id} not found")
    del ITEMS[item_id]
    return {"id": item_id}
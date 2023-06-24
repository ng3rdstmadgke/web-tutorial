[Chapter7] 番外編1: JavaScriptのおさらい
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


# ■ FastAPIで静的ファイルをレスポンスするルートを追加

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

CORS(クロスオリジンリソース共有)を許可しましょう。  
※ 通常、XMLHttpRequestやFetchAPIは異なるオリジンに対してのアクセスをブラウザ側で制限されています。その制限を取り払います。  
参考: [オリジン間リソース共有 (CORS) | MDN](https://developer.mozilla.org/ja/docs/Web/HTTP/CORS)

```python
# --- main.py ---
# ... 略 ...
from fastapi.middleware.cors import CORSMiddleware  # 追加

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # クロスオリジンリクエストを許可するオリジンのリスト。 "*" はすべて許可。
    allow_credentials=True,  # Cookieがクロスオリジンリクエストに対してサポートされるべきかどうか。
    allow_methods=["*"],     # クロスオリジンリクエストで許可されるHTTPメソッドのリスト。 "*" はすべて許可。
    allow_headers=["*"],     # クロスオリジンリクエストで許可されるHTTPヘッダのリスト。 "*" はすべて許可。
)

# ... 略 ...
```

htmlを作成します。
アクセスアクセス

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


# ■ 基本的な文法

## 変数・定数定義

```js
// 変数定義
let a = 100;
let b = "hello";

// 定数
const TAX = 1.10;
```

## 基本的な型

```js
// 数値 (整数も浮動小数点数も同じnumber型として扱われる)
let a = 10;
let b = 123.56;

// 真偽値 (boolean)
let c = true;
let d = false;

// null
let e = null;

// undefined (値が代入されていないという意味)
let f;

// 文字列
let g = "hello";
let g2 = `${g} world`;  // 文字列の中に変数を埋め込むことも可能
console.log(g2);  // "hello world"

// 配列
let h = [[1, 2, 3], ["a", "b", "c"]];
console.log(h[0][1]); // 2
console.log(h[1][2]); // "c"

// オブジェクト
let i = {
    name: "hoge",
    age: 1,
    add: function(a, b) {
        return a + b;
    },
}
console.log(i.name); // "hoge"
console.log(i["name"]); // "hoge"
console.log(i.add(1, 4)); // 5
```

## if文

```js
let flag = null;
if (flag === true) {
    console.log("OK");
} else if (flag === false) {
    console.log("NG");
} else {
    console.log("ERROR");
}
```

## while文

```js
let cnt = 0;
while (cnt < 10) {
    console.log(`cnt = ${cnt}`);
    cnt++;
}
```

## for文

### 普通のfor文

```js
for (let i = 0; i < 10; i++) {
    console.log(`cnt = ${i}`);
}
```

### for in 文

オブジェクトをまわすときに利用します。  
仮引数には `キー` が格納されることに注意。

```js
let data = {apple: 100, banana: 120, cherry: 300};
for (let key in data) {
    console.log(`${key} : ${data[key]}`);
}
```


### for of 文

配列をまわすときに利用します。  
仮引数には `値` が格納されます。

```js
var fruits = ["apple", "banana", "cherry"];
for (var fruit of fruits) {
    console.log(fruit);
}
```

インデックスを使いたい場合は `Object.entries()` を利用します。

```js
let fruits = ["apple", "banana", "cherry"];
for (let [index, fruit] of Object.entries(fruits)) {
  console.log(`${index}: ${fruit}`);
}
```

### forEach

[Array.prototype.forEach()](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach)

forEachを利用した配列のループ

```js
let a = ["a", "b", "c"];
a.forEach((e, i) => {
  console.log(`elem=${e}, index=${i}`)
})

```

forEachを利用したオブジェクトのループ

```js
let o = {apple: 100, banana: 120, cherry: 300};
Object.entries(o)
  .forEach(([k, v]) => {
    console.log(`key=${k}, value=${v}`)
  })
```


## break, continue

```js
let cnt = 0;
while (++cnt) {
    if (cnt % 2 === 0) {
        continue;
    }

    console.log(cnt)

    if (cnt >= 100) {
        break;
    }
}
```

## try, catch, finally

```js
try {
    3 / j;
} catch(e) {
    console.error(e.message); // j is not defined
} finally {
    console.log("complete");
}
```

## throw

```js
throw new Error('Error!!!');
```

## 三項演算子

```js
let flag = 1
let v = flag === 1 ? true : false;
console.log(v);  // true
```

## Null合体演算子 ( `??` )

左側の式が null または undefined の場合に右側の式の値を返し、それ以外の場合に左側の式値を返します。

参考: [Null合体演算子 | MDN](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)


```js
const foo = null ?? 'default string';
console.log(foo);  // 'default string'

const baz = 0 ?? 42;
console.log(baz);  // 0
```

## オプショナルチェーン ( `?.` )

`.` を利用した参照と似ていますが、 `?.` は参照が `null` または `undefined` の場合に、エラーではなく `undefined` を返します。

参考: [オプショナルチェーン | MDN](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Operators/Optional_chaining)


```js
const adventurer = {
  name: 'Alice',
  cat: {
    name: 'Dinah'
  }
};

console.log(adventurer?.cat?.name);  // 'Dinah'

const dogName = adventurer.dog?.name;
console.log(dogName); // undefined

console.log(adventurer.someNonExistentMethod?.()); // undefined
```

# ■ 関数

関数の定義方法は3種類あります。それぞれ特徴があるのですべて把握しておきましょう

## 関数宣言

関数宣言は、JavaScriptがスクリプトやコードブロックを実行するまでに、関数オブジェクトを生成するため、宣言前でも関数を実行することができます。

```js
showMessage("Hello"); //'Hello'

function showMessage(msg) {
  console.log(msg);
}

showMessage("Hello"); //'Hello'
```

## 関数式

関数式は、その式が実行されるときに関数オブジェクトを生成するため、定義された関数の前で関数を呼び出すとエラーを起こします。

```js
showMessage("Hello"); // 'Uncaught ReferenceError: Cannot access 'showMessage' before initialization'

let showMessage = function(msg) {
  console.log(msg);
}

showMessage("Hello"); //'Hello'
```

## アロー関数

関数式と同じく、式が実行されるタイミングで関数オブジェクトが生成されます。

```js
showMessage('Hello'); // 'Uncaught ReferenceError: Cannot access 'showMessage' before initialization'

let showMessage = (msg) => {
  console.log(msg);
}

showMessage('Hello'); //'Hello'
```

関数リテラルとの違いは、定義時に `this` を固定できる点です。  
例えば、下記のコード 。  
`従来の関数` だと実行時の `this` が参照されてしまうため、出力は `undefined` となります。  
`アロー関数` だと宣言時の `this` を参照するため `"時間です！"` が出力されます。  

参考: [従来の関数とアロー関数の違い](https://typescriptbook.jp/reference/functions/function-expression-vs-arrow-functions)

```js
const oneSecond = 1000;

const timer = {
  message: "時間です！",
  start: function () {
    console.log(this); // this は timerオブジェクトを指します。
 
    // 従来の関数
    setTimeout(function () {
      console.log(this.message); // 実行時のthisが参照されます。この場合Windowを指すため、undefindeが出力されます。
    }, oneSecond);
 
    // アロー関数
    setTimeout(() => {
      console.log(this.message); // 定義時のthisが参照されます。この場合timerオブジェクトを指すため "時間です！" が出力されます。
    }, oneSecond);
  },
};

timer.start();
```

※ JavaScriptの `this` は利用場所によって、意味が異なります。

| 場所 | thisの参照先 |
| --- | --- |
| トップレベル(関数の外) | グローバルオブジェクト (window) |
| 関数 | グローバルオブジェクト (window) |
| call/applyメソッド | 引数で指定されたオブジェクト |
| イベントリスナー | イベントの発生元 |
| コンストラクタ | 生成したインスタンス |
| クラスのメソッド | 呼び出し元のオブジェクト |

## デフォルト値

引数にはデフォルト値を設定することができます。

```js
function area(base = 1, height = 2) {
    console.log(base * height);
}

area(); // 2
area(2); // 4
area(5, 5); // 25
area(height = 5); // 10
area(base = 2); // 4
```

## 可変長引数

引数の前に `...` を付与すると、複数の引数を配列として受け取ることができます。

```js
function print(...args) {
    console.log(args.join(" "));
}
print("apple", "banana" ,"cherry"); // "apple banana cherry"
print(...["apple", "banana" ,"cherry"]); // "apple banana cherry" (可変長引数に配列を渡したいとき)
```

# ■ クラス

```js
// 親クラス
// クラス定義(var Member = class { ...}; という書き方もできる)
class Member {
    // コンストラクタ(名前はconstructorで固定)
    constructor(name) {
        // プロパティー(コンストラクタの中に定義する)
        this.name = name;
    }

    // ゲッター(m.name としたときにこの処理を通る)
    get name() {
        return this._name;  // アンダースコアが必要
    }

    // セッター(m.name = "hoge" としたときにこの処理を通る)
    set name(value) {
        this._name = value;
    }

    // メソッド
    getName() {
        return "name : " + this.name;
    }

    // 静的メソッド
    static getLocale() {
        return "ja";
    }
}

// 子クラス
class BusinessMember extends Member { // var BusinessMember = class extends Member {...} という書き方もOK
    constructor(name, clazz) {
        super(name); // 親クラスのコンストラクタは必ず先頭で呼び出す
        this.clazz = clazz;
    }
    getName() { // 親クラスのgetNameをオーバーライド
        return super.getName() + ", class : " + this.clazz;
    }
    work() {
        return this.name + " is working";
    }
}

// 親クラスのコンストラクタの呼び出し
var m = new Member("mido");
// メソッド呼び出し
console.log(m.getName()); // "name : mido"
// セッターの呼び出し
m.name = "midomido";
// ゲッターの呼び出し
console.log(m.name); // "midomido"

// 子クラスのコンストラクタの呼び出し
var bm = new BusinessMember("mido", "Sales");
console.log(bm.name); // mido
console.log(bm.work()); // mido is working
console.log(bm.getName()); // name : mido, class : Sales
```

# ■ DOM操作

DOM(Document Object Model)とはhtmlなどのマークアップ言語を木構造モデルで表現したオブジェクトです。  
JavaScriptではこのDOMをつかって、HTMLの操作を行います。

## ノードの取得

まずはHTMLの特定の要素を取得する方法を見てみましょう。


| メソッド名 | 説明 |
| --- | --- |
| `document.getElementById(id)` | 指定された id 属性を持つ要素を返します。戻り値はライブオブジェクトです。 |
| `document.querySelector(selectors)` | セレクタ式にマッチした要素から最初の一つを取り出します。戻り値はスタティックオブジェクトです。 |
| `document.querySelectorAll(selectors)` | セレクタ式にマッチした要素のNodeListを返します。戻り値はスタティックオブジェクトです。 |

※ ライブオブジェクトとスタティックオブジェクト

- ライブオブジェクト  
ノード取得後にDOMツリーへ加えられた変更を参照できるオブジェクトです。
- スタティックオブジェクト  
ノード取得後にDOMツリーへ加えられた変更は参照できないオブジェクトです。


### `document.getElementById(id)`

```html
<ul id="target" >
    <li>apple</li>
    <li>banana</li>
    <li>orange</li>
</ul>

<script>
    const target = document.getElementById('target');

    // li 要素を追加
    const li = document.createElement('li');
    li.textContent = "lemon"
    target.appendChild(li);

    // li要素に順番にアクセス
    Array.from(target.children).forEach((e, i) => {console.log(`${i}: ${e.textContent}`)});
</script>
```

### `document.querySelector(セレクタ式)` , `document.querySelectorAll(セレクタ式)`


```html
<ul id="target" >
    <li>apple</li>
    <li>banana</li>
    <li>orange</li>
</ul>

<script>
    // querySelectorAll
    const lists = document.querySelectorAll('#target li');
    console.log(lists.length); // 3

    // DOM変更可能
    Array.from(lists).forEach((e, i) => {
      e.textContent = `${i} : ${e.textContent}`;
    })

    // querySelector
    const list = document.querySelector('#target li');
    console.log(list.textContent); // "0: apple"
</script>
```

### セレクタ式

`querySelector` `querySelectorAll` の引数で利用するセレクタ式です。  

| セレクタ | 概要 | 例 |
| --- | --- | --- |
| * | すべての要素 | * |
| #id | 指定したIDの要素 | #target |
| .class | 指定したクラス名の要素 | .js_input |
| elem | 指定したタグ名の要素 | h1 |
| s1, s2, sx | いずれかのセレクタに合致する要素すべて | #main, li, .class |
| parent > child | parent要素の子要素child | #main > div |
| ancestor descendant | ancestor要素の子孫要素descendantをすべて | #list li |
| prev + next | prev要素の直後のnext要素 | #main +div |
| prev ~ siblings | prev要素以降のsiblings兄弟要素 | #main ~ div |
| [attr] | 指定した属性を持つ要素 | input[type] |
| [attr = value] | 属性がvalue値に等しい要素 | input[type = "button"] |
| [attr ^= value] | 属性がvalueから始まる値を持つ要素 | a[href ^= "https://"] |
| [attr $= value] | 属性がvalueで終わる値を持つ要素 | img[src $= ".gif"] |
| [attr *= value] | 属性がvalueを含む値を持つ要素 | [title *= "sample"] |
| [s1][s2][sx] | 複数属性フィルタ全てにマッチする要素 | img[src][alt] |


※ セレクタ式はもともとCSSにおいて、スタイルを適用する要素を選択するためのものです。

```html
<style>
/* id=targetの要素の配下のli要素の色を赤にする */
#target li {
    color: red
}
</style>
```

## ノードオブジェクト

`getElementByID` や `querySelector` で取得したオブジェクトです。

参考: [Node | MDN](https://developer.mozilla.org/ja/docs/Web/API/Node)

### プロパティ

`getElementByID` や `querySelector` で取得した要素が持つプロパティ

| プロパティ名 | 概要 |
| --- | --- |
| parentElement | 親要素ノードへの参照 |
| children | 子要素ノードへの参照を格納する(HTMLCollection) |
| firstElementChild | 最初の子要素ノード |
| lastElementChild | 最後の子要素ノード |
| nextElementSibling | 次の兄弟要素ノード |
| previousElementSibling | 一つ前の兄弟要素ノード |
| childElementCount | 子要素ノードの数(=children.length) |

```html
<div>
  <ul id="target" >
      <li>apple</li>
      <li>banana</li>
      <li>orange</li>
  </ul>
</div>

<script>
  let ul = document.getElementById("target");

  console.log(ul.parentElement);  // <div>...<div>
  console.log(ul.children);  // HTMLCollection(3) [li, li, li]
  console.log(ul.firstElementChild);  // <li>apple<li>
  console.log(ul.lastElementChild);  // <li>orange<li>
  console.log(ul.firstElementChild.nextElementSibling);  // <li>banana<li>
  console.log(ul.lastElementChild.previousElementSibling);  // <li>banana<li>
  console.log(ul.childElementCount);  // 3
</script>
```

### テキストの操作

要素のテキストノード ( `<div>ここがテキストノード</div>` )を操作するには `textContent` や `innerHTML` を利用します。

- `textContent`  
テキストノードをプレーンテキストとして扱います。
- `innerHTML`  
テキストノードをHTMLとして扱います。

```html
<ul id="list">
    <li id="first">google</li>
    <li id="second">yahoo</li>
</ul>

<script>
var list = document.getElementById("list");

// --- textContent ---
// 取得
console.log(list.textContent); // 子要素それぞれからテキストだけ取出す(google\nyahoo)
// 設定
var first = document.getElementById("first");
first.textContent = '<span style="color: Red;">hello</span>'; // テキストとしてセットされる


// --- innerHTML ---
// 取得
console.log(list.innerHTML); // htmlとして取出す(<li>google</li>\n<li>yahoo</li>)
// 設定
var second = document.getElementById("second");
second.innerHTML = '<span style="color: Red;">hello</span>'; // htmlとしてセットされる
</script>
```


### 属性の操作

属性へのアクセスは `要素ノード.属性名` を利用します。

<font color="red">※ class属性を取得するときは `要素ノード.className` とする必要があります</font>

```html
<form id="form">
    <input class="js_input" type="text" value="default"/>
</form>

<script>
var f = document.getElementById("form");
var input = f.firstElementChild
console.log(input.value); // default
console.log(input.className); // js_input
input.value = "set attribute";  // 入力フォームが更新される
</script>
```

そのほかにも、 `getAttribute(属性名)` `setAttribute(属性名, 値)` を利用したアクセスが可能です。  
※ ただし、 `getAttribute` `setAttribute` はユーザーからの入力で変更された値を受け取れないので、input要素などユーザーからの入力がある要素で利用してはいけません。

```html
<ul id="fruits">
    <li data-id="1" class="js_fruit">apple</li>
    <li data-id="2" class="js_fruit">banana</li>
    <li data-id="3" class="js_fruit">orange</li>
</ul>

<script>
var ul = document.getElementById("fruits");
var li = ul.firstElementChild
console.log(li.getAttribute("data-id")); // 1
console.log(li.getAttribute("class")); // js_fruit
li.setAttribute("data-id", "5");  // appleのdata-idが更新される
console.log(li.getAttribute("data-id")); // 5
</script>
```

# ■ イベント

JavaScriptでは画面上で行われたさまざまな操作に紐づけて処理を行うことができます。  
これらの操作を `イベント` と呼び、イベントにはクリック、フォームの変更、マウスの移動など様々な種類があります。  

イベントの発生を監視する仕組みを `イベントリスナー` と呼び、 `elem.addEventListener("イベント", 関数)` のように設定します。( `elem` で `イベント` が発生したときに `関数` が実行されます。)

```html
<input id="js_button" type="button" value="アラート表示"/>

<script>
document.getElementById("btn").addEventListener("click", function(event){
    window.alert("ボタンがクリックされました");
});
</script>
```

## イベントの種類

`addEventListener` の第一引数に指定できるイベントには、下記のようなものがあります。

参考: [イベント一覧 | MDN](https://developer.mozilla.org/ja/docs/Web/Events)

| イベント名 | 発生タイミング |
| --- | --- |
| DOMContentLoaded | ページ/画像の読み込みが完了したとき |
| unload | 他のページに移動するとき |
| click | クリック時 |
| dblclick | ダブルクリック時 |
| mousedown | マウスボタンを押したとき |
| mouseup | マウスボタンを離したとき |
| mousemove | マウスポインターが移動したとき |
| mouseenter | マウスポインターが要素に乗ったとき(対象要素の出入りに際して発生) |
| mouseleave | マウスポインターが要素から外れたとき(対象要素の出入りに際して発生) |
| keydown | キーを押したとき |
| keypress | キーを押しているとき |
| keyup | キーを離したとき |
| change | フォームなどの内容が変更されたとき |
| reset | リセットボタンを押したとき |
| submit | サブミットボタンを押したとき |
| blur | 要素からフォーカスが離れたとき |
| focus | 要素がフォーカスされたとき |
| scroll | スクロールしたとき |

## イベントオブジェクト

`addEventListener` の第二引数の関数は引数として `event` オブジェクトを受け取ります。  
イベントオブジェクトから、イベント発生時の様々な情報にアクセスすることができます。

```
event.cancelable : イベントがキャンセル可能か
event.defaultPrevented : preventDefaultメソッドが呼ばれたか
event.target : イベント発生元の要素
event.currentTarget: イベントを設定した要素
event.type : イベントの種類(click, mouseover等)
event.timeStamp : イベントの作成日時
event.screenX : イベントの発生座標(デスクトップ上でのX座標)
event.screenY : イベントの発生座標(デスクトップ上でのY座標)
event.pageX : イベントの発生座標(ページ全体上でのX座標)
event.pageY : イベントの発生座標(ページ全体上でのY座標)
event.clientX : イベントの発生座標(ブラウザの表示領域上でのX座標)
event.clientY : イベントの発生座標(ブラウザの表示領域上でのY座標)
event.offsetX : イベントの発生座標(要素上でのX座標)
event.offsetY : イベントの発生座標(要素上でのY座標)
event.button : マウスのどのボタンが押されているか(0 : 左, 2 : 右, 1 : 中央)
event.key : 押下されたキーボードのキーの値
event.keyCode : 押下されたキーのコード
event.altKey : Altが押下されているか
event.ctrlKey : Ctrlが押下されているか
event.shiftKey : Shiftが押下されているか
```

```html
<form>
  <input id="js_text" type="text" value="">
</form>

<script>
document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("js_text").addEventListener("change", function(event){
      let elem = event.currentTarget;
      window.alert(`入力値: ${elem.value}`);
  });
})
</script>
```

## イベント本来の挙動のキャンセル

イベント本来の挙動とは、 `a` タグなら「ページを移動する」 `submit` ボタンなら「フォームを送信する」など、ブラウザ標準で決められた動作のことです。  
これらの、デフォルトの挙動をキャンセルするには `event.preventDefault()` を利用します。  


```html
<form id="js_form">
  <input type="text" value="">
  <input type="submit" value="送信">
</form>

<script>
document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("js_form").addEventListener("submit", function(event){
    // デフォルトの挙動をキャンセル
    event.preventDefault();
    if (!window.confirm("本当に送信しますか？")) {
      return
    }
    Array.from(event.currentTarget.children).forEach((elem, i) => {
      console.log(`${i}: ${elem.value}`);

    });
  });
})
</script>
```

# ■ Cookieの取り扱い

Cookieとはリクエスト時にCookieヘッダに設定される小さいテキスト情報です。  
ログインセッション等の一時的な情報をサーバーとやり取りするために利用されます。  



## Cookieの追加

cookieは `key=value` 形式で登録します

```html
<script>
document.cookie = "name=mido";
console.log(document.cookie);  // name=mido

// 追加
document.cookie = "age=32";
console.log(document.cookie);  // name=mido; age=32

// "=" ";" マルチバイト文字など、cookieに登録できない文字を含む場合
document.cookie = "hoge=" + encodeURIComponent("=;太郎");
console.log(document.cookie);  // age=32; name=mido; hoge=%3D%3B%E5%A4%AA%E9%83%8E
</script>
```

## Cookieの削除

Cookieの削除は、削除したいキーの有効期限を0にすることで行えます。  
`max-age` を0にする方法と、 `expires` を過去の日付にする方法があります。  

- max-age  
cookieの残存期間を秒数で指定します。
- expires  
GMT形式の日付を指定します。GMT形式への変換は、toUTCString関数で行うことができます。

```html
<script>
// cookieの残存期間を0にすることで削除
document.cookie = "name=; max-age=0";

// cookieの有効期限を過去の日付にすることで削除
let date = new Date("1990-12-25")
document.cookie = "name=; expires=" + date.toUTCString();
</script>
```

## Cookieの取得

JavaScript自体にはいい感じCookieをパースして、辞書のようにアクセスできるAPIが実装されていないので自作します。

```html
<script>
function getCookie(key) {
  let obj = Object.fromEntries(
    document.cookie
      .split(";")
      .map((e) => {
        return e.trim()
          .split("=")
          .map((k) => {
            return decodeURIComponent(k);
          });
      })
  );
  return obj[key];
}

getCookie("name")  // 'mido'
getCookie("hoge")  // '=;太郎'
</script>

```


# ■ ローカルストレージ
ローカルストレージとはオリジン単位でブラウザ側にデータを保存しておく機能です。  
ウィンドウ・タブをまたいでデータの共有が可能でブラウザを閉じてもデータは維持されます。

※ オリジンとは`スキーマ://ホスト名:ポート` のこと

```js
var storage = localStorage; // ローカルストレージオブジェクト
```

## データの取得・保存

オブジェクトのように、 Key-Value形式でデータを保存・取得することができます。  

```js
// 保存
storage.name = "ktamido";
storage["年齢"] = "32歳";
storage.setItem("職業", "エンジニア");

// 取得 
console.log(storage.name);  // ktamido
console.log(storage["年齢"]);  // 32歳
console.log(storage.getItem("職業"));  // エンジニア
```

## データの削除

```js
// 指定したキーを削除
delete storage.name;
delete storage["年齢"];
storage.removeItem("職業");

// すべてのデータを破棄
storage.clear();
```

## オブジェクトを保存する

オブジェクトを保存する場合はjsonに変換して保存しましょう。
※ メソッドは保存できません。

```js
var storage = localStorage;
// 保存
var apple ={name: "りんご", price: 150} 
storage["apple"] = JSON.stringify(apple);
// 取得
var data = JSON.parse(storage.getItem("apple"));
console.log(data);  // {name: "りんご", price: 150}
```

## ストレージの変更を監視する

ストレージの変更を監視する場合は `storage` イベントを利用します。

```js
window.addEventListener("storage", function(e) {
    console.log(e.key); // 変更されたキー
    console.log(e.oldValue); // 変更前の値
    console.log(e.newValue); // 変更後の値
    console.log(e.url); // 発生元ページ
}, false);
```

# ■ 非同期

# ■ そのほかよく使うもの

## アラート

アラートダイアログを表示します。

```js
alert("エラーが発生しました！")
```

## 確認ダイアログ

OKをクリックすると `true` 、 キャンセルをクリックすると `false` を返します。

```html
<input id="btn" type="button" value="確認">

<script>
document.getElementById("btn").addEventListener("click", function(e) {
    if (window.confirm("confirm")) {
        console.log("OK")
    } else {
        console.log("Cancel")
    }
});
</script>
```

## locationオブジェクト

表示ページのアドレス情報を取得/操作することができます。

```現在のURL
http://example.com:8080/js/sample.html#gihyo?id=12345
```

| メンバー | 概要 | 戻り値の例 |
| --- | --- | --- |
| hash | アンカー名 | #gihyo?id=12345 |
| host | ホスト | example.com:8080 |
| hostName | ホスト名 | example.com |
| origin | オリジン | http://example.com:8080 |
| href | リンク先 | http://example.com:8080/js/sample.html#gihyo?id=12345 |
| pathname | パス名 | js/sample.html |
| port | ポート | 8080 |
| protocol | プロトコル | http: |
| search | GETパラメータ | ?id=12345 |
| reload() | 再読込 |  |
| replace(url) | 指定ページurlに移動 |  |


location.hrefにURLを設定することでページ遷移が可能です。

```js
location.href = "http://localhost:8018/index.html";
```

## JSON

JSONとオブジェクトの変換ができます

```js

let data = {"name": "mido", "age": 32}

// オブジェクトをjsonに変換
let json = JSON.stringify(data);


// jsonをオブジェクトに変換
let obj = JSON.parse(json);
```

# ■ リクエストの送信

APIにリクエストを送信するには `fetch()` を利用します。

```
fetch(url [, options])
  - url: アクセスするURL
  - options: リクエストオプション
    - method: リクエストメソッド(GET, POST, PUT, DELETE)
    - headers: リクエストヘッダ ({"Content-Type": "application/json", ...})
    - body: リクエストボディ (FormData, Blob, URLSearchParamsなど)
    - redirect: リダイレクトの方法
      follow: 自動でリダイレクト (default)
      error: リダイレクト時はエラー
      manual: 手動でリダイレクト処理
```

`fetch` メソッドの戻り値は `Promise<Response>` オブジェクトです。  
`then` メソッドで受け取る引数の `Response` オブジェクトには下記のようなメンバーが用意されています。

```
## プロパティ
- ok: 成功したかどうか
- redirected: レスポンスがリダイレクトの結果であるかどうか
- status: HTTPstatusコード
- statusText: statusメッセージ
- headers: レスポンスヘッダ
- url: レスポンスのURL
- body: レスポンスボディ (ReadableStreamオブジェクト)

## メソッド (これらのメソッドの戻り値はPromiseオブジェクトなので、thenで結果を受け取らなければならない)
- arrayBuffer(): レスポンスボディをArrayBufferとして取得
- blob(): レスポンスボディをBlobとして取得
- formData(): レスポンスボディをFormDataとして取得
- json(): レスポンスボディをJSONとして取得
- text(): レスポンスボディをテキストとして取得
```


## GETリクエストの場合

```js
fetch("http://example.com/items/", {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${jwtToken}`,  // 認証情報(jwtトークン)の設定
  },
}).then((response) => {
  if (!response.ok) {
    // レスポンスが200以外ならエラー
    throw new Error(`${response.status} ${response.statusText}`)
  }
  // json() の戻り値は Promise なのでthen()で結果を受け取る
  return response.json()
}).then((json) => {  // 成功時の処理
  console.log(json)
}).catch((error) => {  // エラー時の処理
  console.log(error.message)
})

```

## POSTリクエストの場合

```js
/**
 * ボディにFormDataを指定する場合
 */
let form = document.getElementById("js_form")
fetch("http://example.com/items/", {
  method: "POST",
  body: new FormData(form),
  headers: {
    "Authorization": `Bearer ${jwtToken}`,  // 認証情報(jwtトークン)の設定
  },
}).then((response) => {
  if (!response.ok) {
    // レスポンスが200以外ならエラー
    throw new Error(`${response.status} ${response.statusText}`)
  }
  return response.json()
}).then((json) => {  // 成功時の処理
  console.log(json)
}).catch((error) => {  // エラー時の処理
  console.log(error);
})


/**
 * ボディにJSONを指定する場合
 */
fetch("http://example.com/items/", {
  method: "POST",
  body: JSON.stringify({
    "title": "hogehoge",
    "content": "fugafuga",
  }),
  headers: {
    "Content-Type": "application/json",  // JSONをbodyにする場合は必須
    "Authorization": `Bearer ${jwtToken}`,  // 認証情報(jwtトークン)の設定
  },
}).then((response) => {
  if (!response.ok) {
    // レスポンスが200以外ならエラー
    throw new Error(`${response.status} ${response.statusText}`)
  }
  return response.json()
}).then((json) => {  // 成功時の処理
  console.log(json)
}).catch((error) => {  // エラー時の処理
  console.log(error);
})

```

## ログインとユーザー一覧を表示するWebページを実装してみましょう

Cookieを登録・取得できるユーティリティーを実装しましょう。

```js
// --- static/util.js ---
window.CookieUtil = {
  getCookie: function(key) {
    let obj = Object.fromEntries(
      document.cookie
        .split(";")
        .map((e) => {
          return e.trim()
            .split("=")
            .map((k) => {
              return decodeURIComponent(k);
            });
        })
    );
    return obj[key];
  },
  setCookie: function(key, value) {
    document.cookie = encodeURIComponent(key) + "=" + encodeURIComponent(value);
  }
}
```


ログイン画面の実装

```html
<!-- static/login.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="/util.js"></script>
  <title>Document</title>
</head>
<body>
<div>
  <ul>
    <li><a href="/items/index.html">アイテム一覧</a></li>
  </ul>
</div>

<form id="js_form">
  <div>
    <label ref="js_username">username</label>
    <input id="js_username" name="username" type="text" value="" required>
  </div>
  <div>
    <label ref="js_password">password</label>
    <input id="js_password" name="password" type="password" value="" required>
  </div>
  <div>
    <input type="submit" value="送信">
  </div>
</form>

<!-- リクエスト結果の表示エリア ここから -->
<div id="js_result">
</div>
<!-- リクエスト結果の表示エリア ここまで -->

<script>
document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("js_form").addEventListener("submit", function(event){
    let result = document.getElementById("js_result");
    let form = event.currentTarget;
    if (!form.reportValidity()) {
      return
    }

    // デフォルトの挙動をキャンセル
    event.preventDefault();

    fetch("/api/v1/token", {
      method: "POST",
      body: new FormData(form),
    }).then((response) => {
      if (!response.ok) {
        // json() の戻り値は Promise なので、さらに then() で結果を受け取る
        throw new Error(`ログイン失敗 (${response.statusText})`)
      }
      return response.json()
    }).then((json) => {
      let token = json.access_token;
      CookieUtil.setCookie("token", token)
      result.textContent = `ログイン成功 (token=${token})`
    }).catch((error) => { // エラー発生時の処理
      result.textContent = error.message
      console.log(error);
    });
    result.textContent = "通信中...";
  });
})
</script>
</body>
</html>

```

アイテム一覧画面の実装します。

```html
<!-- static/items/index.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="/util.js"></script>
  <title>Document</title>

</head>
<body>

<div>
  <ul>
    <li><a href="/login.html">TOP</a></li>
    <li><a href="/items/create.html">アイテム登録</a></li>
  </ul>
</div>

<!-- リクエスト結果の表示エリア ここから -->
<div id="js_result">
</div>
<!-- リクエスト結果の表示エリア ここまで -->

<script>
/**
 * li要素を作成する
 */
function createListElem(item) {
  let li = document.createElement("li")
  li.setAttribute("id", item.id)
  li.textContent = `title=${item.title} content=${item.content}`;
  return li
}

// ページの読み込みが完了したら発火
document.addEventListener("DOMContentLoaded", function() {
  let result = document.getElementById("js_result");
  fetch("/api/v1/items/", {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${CookieUtil.getCookie("token")}`,
    },
  }).then((response) => {
    if (!response.ok) {
      throw new Error(`アイテム一覧取得失敗 (${response.statusText})`)
    }
    return response.json()
  }).then((items) => {
    // 取得したユーザー一覧でli要素を作成して、ul要素に追加
    result.innerHTML = '';
    for (let item of items) {
      let li = createListElem(item);
      result.appendChild(li);
    }
  }).catch((error) => {
    result.innerHTML = '';
    result.textContent = error.message
    console.log(event);
  })
  result.textContent = "通信中...";

})
</script>
</body>
</html>

```

アイテムを登録する画面を実装します。

```html
<!-- static/items/create.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="/util.js"></script>
  <title>Document</title>

</head>
<body>

<div>
  <ul>
    <li><a href="/login.html">TOP</a></li>
    <li><a href="/items/index.html">アイテム一覧</a></li>
  </ul>
</div>

<form id="js_form">
  <div>
    <label ref="js_title">title</label>
    <input id="js_title" name="title" type="text" value="" required>
  </div>
  <div>
    <label ref="js_content">content</label>
    <input id="js_content" name="content" type="text" value="" required>
  </div>
  <div>
    <input type="submit" value="登録">
  </div>
</form>

<!-- リクエスト結果の表示エリア ここから -->
<div id="js_result">
</div>
<!-- リクエスト結果の表示エリア ここまで -->
<script>
document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("js_form").addEventListener("submit", function(event){
    let result = document.getElementById("js_result");
    let form = event.currentTarget;
    if (!form.reportValidity()) {
      return
    }

    // デフォルトの挙動をキャンセル
    event.preventDefault();

    fetch("/api/v1/items/", {
      method: "POST",
      body: JSON.stringify({
        "title": document.getElementById("js_title").value,
        "content": document.getElementById("js_content").value,
      }),
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${CookieUtil.getCookie("token")}`,
      },
    }).then((response) => {
      if (!response.ok) {
        // json() の戻り値は Promise なので、さらに then() で結果を受け取る
        throw new Error(`アイテム登録失敗 (${response.statusText})`)
      }
      location.href = location.origin + "/items/"
    }).catch((error) => {
      result.textContent = error.message
      console.log(error);
    })
    result.textContent = "通信中...";
  });
})
</script>
</body>
</html>

```


http://localhost:8018/login.html にアクセスしてみましょう。
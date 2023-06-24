[Chapter8] 番外編2: TypeScriptのおさらい
--
[top](../../README.md)

# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter8/src` をルートディレクトリとして解説します。

Chapter8では、TypeScriptに触れていきましょう。  

今日、JavaScriptはWebサイトで必ず利用されているといっても過言ではない言語ですが、それはJavaScriptが「優れた言語」だからではありません。  
単にメジャーなブラウザで共通して動作する言語がJavaScriptしかないからです。 (つまり選択肢がないので、仕方なく利用しているのです。)
ひと昔前まではjQueryなどのライブラリを利用し、JavaScriptに足りない機能を補いブラウザごとの微妙な差を埋めるという手法でJavaScriptのイケてなさを隠ぺいするのが主流でした。  
しかし、最近ではJavaScriptのイケてない言語仕様自体を隠ぺいするため、JavaScriptに変換(トランスパイル)可能な新しい言語を利用するといった手法が主流となっています。(JavaScriptにトランスパイル可能な代替言語をaltJSといいます。)  
TypeScriptはこのaltJSの一つで、近年のデファクト・スタンダードとなっている言語です。


参考

- [TypeScript Docs](https://www.typescriptlang.org/docs/)
- [サバイバルTypeScript](https://typescriptbook.jp/)


# ■ アプリの起動

```bash
# ※ 起動していない場合のみ
./bin/mysql.sh

# 開発用shellを起動
./bin/run.sh chapter8 --mode shell

# データベースの初期化
./bin/init-database.sh

exit

# アプリを起動
./bin/run.sh chapter8 --mode app
```

http://127.0.0.1:8018/ にブラウザでアクセス


# ■ 開発用shellを起動しましょう

```bash
# 開発用shellを起動
./bin/run.sh chapter8 --mode shell
```

# ■ TypeScriptの環境準備

```bash
# node.jsがインストールされているか確認
node -v

# npmのアップデート
sudo npm update -g npm

# プロジェクト作成
mkdir static/ts_tutorial
cd static/ts_tutorial

# プロジェクトを初期化してTypeScriptをインストール
npm init --y
npm install typescript

# ./node_modules配下に typescript がインストールされているはずです。
ls ./node_modules

# TypeScriptのトランスパイラは ./node_modules/typescript/bin 配下にあります。
ls ./node_modules/typescript/bin/tsc

# node_modules配下のコマンドを利用するには npx コマンドを利用します。
# tscコマンドのヘルプを表示してみましょう
npx tsc -h
```

簡単なプログラムを作成してみましょう


```ts
// --- static/ts_tutorial/hello.ts ---
function add(a: number, b: number): number {
  return a + b
}

console.log(add(1, 1))
```

```bash
# .ts を .js にトランスパイル (ビルド)
# --outDir <PATH>
#   ビルドしたファイルをを配置するディレクトリ
npx tsc hello.ts --outDir tmp

# ビルドを行うと tmp/hello.js が生成されます。
cat tmp/hello.js

# 実行
node tmp/hello.js
```

次はビルドしたファイルをhtmlから読み込んでみましょう

```html
<!-- --- static/index.html --- -->
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<body>
  <h1>Hello World</h1>

  <!-- hello.ts -->
  <script src="/ts_tutorial/tmp/hello.js"></script>
  <script>
    let v = add(100, 200)
    console.log("v: ", v)
  </script>
  <!-- hello.ts -->

</body>
</html>
```

http://localhost:8018/ にブラウザでアクセス


# ■ TypeScriptの型

`Type` の名の通り、TypeScriptはJavaScriptに型指定を追加した言語です。つまり、静的な型システムを備えたJavaScriptといったところです。  
加えてTypeScriptはJavaScriptのスーパーセット(拡張構文)なので、JavaScriptで書いたコードはほぼそのままTypeScriptとして動作します。  

※ 以降の動作確認は [TypeScript Playground](https://www.typescriptlang.org/play) を利用すると便利です。

## 変数・定数の定義

```typescript
# 変数の定義
let a: string = "hoge";

# 定数の定義
const b: string = "fuga";
```

## プリミティブ型　

```typescript
// プリミティブ型
let a: string = "hoge";
let b: number = 90; // 0xFF, 0b1111, 0o666とかでもOK
let c: boolean = true;
let d: null = null;
let e: undefined = undefined;
let f: any = "hoge"; // 何でもいい
```


## 配列型

```ts
// 配列
let g: string[] = ["java", "php", "python"];
let h: number[][] = [[1,2,3], [4,5,6], [7,8,9]];
console.log(g[1]); // php
```
## タプル型

タプルは要素が固定された配列を表す型です。(JavaScriptには存在しない概念です)

```ts
// タプル
let role: [number, string] = [2, "author"];

// 読み取り専用のタプルを定義することもできる
let data: readonly[string, number, boolean] = ["hgoe", 10, false];
```

## 連想配列型

```ts
// 連想配列
let i: { [index: string]: number } = {"a": 1, "b": 2};
console.log(i["a"]); // 1
console.log(i.a);    // 1

// インターフェースを利用した書き方
interface StringMap {
    [index: string]: string;
}

let map: StringMap = { "key": "value"};
```

## オブジェクト型

オブジェクト型のリテラル

```ts
let c1: {type: string, weight: number, run(): string } = {
    type: "car",
    weight: 1500,
    run() {
        return `${this.type} is running`;
    }
}
console.log(c1.type); // car
console.log(c1.weight); // 1500
console.log(c1.run()); // car is running.
```


interfaceを利用した型指定 (詳しくは後述)

```ts
interface Car {
    // プロパティシグニチャ
    type: string;
    weight: number;
    // メソッドシグニチャ
    run(): void;
}

let c2: Car = {
    type: "トラック",
    weight: 3000,
    run() {
        console.log(`${this.type} is running.`);
    }
}

console.log(c2.type); // トラック
console.log(c2.weight); // 3000
console.log(c2.run()); // トラック is running.
```


## 関数型

```ts
// 関数
let l: (a: number, b: number) => number = function(a: number, b: number): number {
    return a + b;
}

// interfaceを利用した型指定
interface CarShow {
    (type: string, weight: number): string;
}

let c: CarShow = function(type: string, weight: number): string {
    return `${type}: ${weight}`;
}
```

## Union型 (共用型)

複数の方のうちのどれかを表す型です。

```ts
// Union型 (共用型)
let j: string | null = "fuga";
j = null;
let k: (string | number)[] = ["hgoe", 0, 1];
```

## enum

```ts
enum IndexType {
    UPLOAD      = 1,
    CRAWL       = 2,
    DIFF_UPLOAD = 3,
    DIFF_CRAWL  = 4
}

let indexType: IndexType = IndexType.CRAWL;
console.log(indexType); // 2
```

## リテラル型

特定の文字列をそのまま型として利用できる仕組みを文字列リテラル型といいます。

```ts
type Season = 'spring' | 'summer' | 'autumn' | 'winter';

function getScene(s: Season) {
  console.log(s);
}

getScene('sprint'); // OK
getScene('fall'); // エラー
```

文字列以外にもリテラル型は存在します。

```ts
// falsyな値
type FalsyType = '' | 0 | false | null | undefined;

// さいころの目
type DiceType = 1 | 2 | 3 | 4 | 5 | 6;

// Enumの一部分
enum Subject { JAPANESE, MATCH, SCIENCE, SOCIAL_STUDY, ENGLISH }
type SciencePart = Subject.MATH | Subject.SCIENCE;
```

**リテラル型と型推論**

```ts
const a = 10;  // constで定義するとリテラル型の 10 とみなす
let b = 10;  // letで定義すると number型 とみなす
```

## 型エイリアス

特定の方に対して別名を付与する仕組み。主に**タプル型**や**共用型**などに対して短い名前を付ける用途で利用されます。

<font color="red">※ 基本的にインターフェイスで表現出来る型はインターフェイスを利用するべきです</font>

```ts
type FooType = [string, number, boolean];
let data: FooType = ["abc", 9, true];

type HogeType = number | boolean;
let hoge: HogeType = 1;
```

## null非許容型・null許容型
`tsconfig.json` (TypeScriptの設定ファイル) で`strict` または `strictNullChecks` オプションを `true` に設定すると、すべての型で `null` `undefined` を禁止できます。 この `null` `undefined` を禁止された型を null非許容型 と呼びます。

`null` `undefined` を許容したい場合は下記のように、Union型を利用して指定します。(null許容型)

```ts
let data1: string | undefined = undefined;
let data2: string | null = null;
```

### # `!.` 演算子 (非nullアサーション演算子)

[ 非Nullアサーション (non-null assertion operator) | サバイバルTypeScript ](https://typescriptbook.jp/symbols-and-keywords#-%E9%9D%9Enull%E3%82%A2%E3%82%B5%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3-non-null-assertion-operator-ts)

値が `null` や `undefined` でないことを宣言し、コンパイラーに値を非Nullとして解釈させます。

```ts
function firstChar(text: string | undefined): string {
  // コンパイルエラーにならない
  return text!.charAt(0);
}

console.log(firstChar("Hello")) // "H"
console.log(firstChar())  // 実行時にエラーになる
```


### # `?.` 演算子 (オプショナルチェーン)

[# オプショナルチェーン (?.) | MDN](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Operators/Optional_chaining)

null許容型のメンバーにアクセスする際は `null` `undefined` チェックが必要になるが、 `?.` 演算子を利用することで下記のように実装することができます。

```ts
function firstChar(text: string | undefined): string | undefined {
  // オブジェクトがnull/undefined以外の時にだけcharAtにアクセスする。
  // null/undefinedの場合はundefinedを返す。
  return text?.charAt(0);
}

console.log(firstChar("Hello"))  // "H"
console.log(firstChar())  // undefined
```

### # `??` 演算子 (Null合体演算子)
[# Null 合体演算子 (??) | MDN](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)

`null` `undefined` の場合のみ規定値を設定する

```ts
let len = str?.length ?? 0;
```


# ■ インターフェース を利用した型注釈

TypeScriptではinterfaceを型注釈として利用することができます。

## プロパティシグニチャ

プロパティシグニチャでは、 `?` で省略可能なプロパティを、 `readonly` で読み取り専用のプロパティを表すこともできます。

```ts
interface Person {
  name: string;
  age?: number;  // 省略可能
  readonly gender: "male" | "female";  // 読み取り専用
}

// ageは省略可能
let p: Person = { name: "midorikawa", gender: "male" };

// nameへの代入は不可
p.gender = "female"; // コンパイルエラー
```

## コールシグニチャ

関数型を宣言するためのシグニチャです。  
`(引数: 型, ...): 戻り値の型` で表します。

```ts
interface Calculate {
    (x: number, y: number): number;
}
let add: Calculate = function(a: number, b: number): number { return a + b }

console.log(add(2, 3));
```

## メソッドシグニチャ

メソッドの型を宣言するためのシグニチャです。  
`メソッド名(引数: 型, ...): 戻り値の型` のように表します。

```ts
interface Calculate {
    add(x: number, y: number): number;
}

let obj: Calculate = {
    add(a: number, b: number): number { return a + b }
}

console.log(obj.add(1, 2));
```

## インデックスシグニチャ

連装配列を宣言するためのシグニチャ

```ts
interface NumberAssoc {
    [index: string]: number;
}

let list: NumberAssoc = {
    'hundred': 100,
    'thousand': 1000,
}
```

## コンストラクタシグニチャ

`new` を利用することでコンストラクタの型を宣言できます。  
例えば、以下は number, number型の二つの引数を受け取り、Triangle型を生成するコンストラクタ型の宣言です。

```ts
interface Figure {
    new(width: number, height: number): Triangle;
}

class Trianble {
    constructor(private width: number, private height: number) {}
}

let Tri: Figure = Triangle;
```

# ■ 変数の型判定 (型ガード)

## プリミティブ型の判定

`typeof` 演算子を利用します。

```ts
function process(value: string | number) {
  if (typeof value === "string") {
    return value.toUpperCase()
  } else {
    return value.toFixed(1);
  }
}
```

## クラス型の判定

`instanceof` 演算子を利用します。

```ts
if (obj instanceof Person) { ... }
```

オブジェクトが特定のメンバを持つかを確認することも可能です。

```ts
if ('name' in obj) { ... }
```

## 型判定のサンプル

```ts
class Sample {
}
// typeofはプリミティブ型の判定に用いる
console.log(typeof "value"); // string
console.log(typeof 9); // number
console.log(typeof true); // boolean
console.log(typeof null); // object
console.log(typeof undefined); // undefined
console.log(typeof (new Date())); // object
console.log(typeof (new Sample())); // object
console.log(typeof ["hoge", "fuga"]); // object

// instanceofはオブジェクトがどのコンストラクタから生成されたかを判別する
// console.log("hoge" instanceof string); // エラー
// console.log(9 instanceof number); // エラー
// console.log(true instanceof boolean); // エラー
console.log((new Date()) instanceof Date); // true
console.log(["hoge", "fuga"] instanceof Array); // true
console.log({"hoge": 1, "fuga": 2} instanceof Object); // true
console.log((new Sample()) instanceof Sample); // true
```


# ■ 関数定義

```typescript
// function命令
function add(a: number, b: number): number {
	return a + b;
}

// 関数リテラル(型指定は省略できる)
let add: (a: number, b: number) => number = function(a: number, b: number): number {
    return a + b;
}

// アロー関数(型指定は省略できる)
// アロー関数はthisを固定する。アロー関数は宣言された地点のthisが関数内に固定される。
let join: (a: string, b: string) => string = (a: string, b: string): string => {
    return a + " " + b;
}
```

## 関数の戻り値として利用するデータ型

- void
値を返さない型
- never
館数が常に例外を発生するとか、無限ループになっているなど、終点に到達できないことを示す。

## デフォルト引数

引数の後ろに ` = 値` を指定すると、実行時にその引数を省略することができます。

```typescript
function showTime(prefix: string = "time: ", time: Date = new Date()): string {
    return prefix + time.toLocaleString();
}

// デフォルト引数は省略できる
console.log(showTime());
console.log(showTime("日時: "));

// 前方のデフォルト引数を省略したい場合はundefinedを指定する
// ※ undefinedは未指定扱いだが、nullは指定扱いになる
console.log(showTime(undefined, new Date("2020-01-01")));
```
## 可変長引数

仮引数の前に `...` を付与することで可変長引数となります。  
可変長引数は渡された任意の個数の引数を配列としてまとめて受け取る機能です。

```typescript
function sum(...ns: number[]): number {
    return ns.reduce((ret: number, e: number) => ret + e);
}

console.log(sum(1,2,3,4,5));
// console.log(sum([1,2,3,4,5])); // エラー
```

## オプション引数

https://typescriptbook.jp/reference/functions/optional-parameters

オプション引数(optional parameter)は、渡す引数を省略できるようにするTypeScript固有の機能です。  
オプション引数は引数名の後ろに `?` を書くことで表現します。 オプション引数は省略すると `undefined` となります。

```ts
function 関数名(引数名?: 型) {}
//                  ^オプション引数の標示
```

```ts
function sample(a?: string) {
  console.log(a)
}

sample("hoge")  // hoge
sample()  // undefined
```

# ■ クラス

## クラス定義

アクセス修飾子には下記が利用できます。

- public: クラスの外からも自由にアクセス可能 (default)
- protected: 同じクラス、または派生クラスのメンバからのみアクセス可能
- private 同じクラスからのみアクセス可能

※ `tsconfig.json` の `strict` `strictPropertyInitialization` を有効化するとコンストラクタの引数が足りない時にエラーにできます。

```typescript
class Person {
    // プロパティ
    private _age: number = 0;
    private name: string;
    private sex: string;

    // 静的プロパティ
    public static Pi: number = 3.14;

    // コンストラクタ(コンストラクタの仮引数は自動的にプロパティになる)
    constructor(private name: string, private sex: string) {
    }
    // コンストラクタは下記のように実装してもよい
    constructor(name: string, sex: string) {
        this.name = name;
        this.age = age;
    }

    // メソッド
    public show(): string {
        return `${this.name}(${this._age}): ${this.sex}`;
    }

    // 静的メソッド
    public static circle(r: number): number {
        return r * r * this.Pi;
    }

    // ゲッター
    get age(): number{
        return this._age;
    }

    // セッター
    set age(value: number) {
        this._age = value;
    }
}

let p = new Person("mido", "mail");
// プロパティ呼び出し
console.log(p.name); // "mido"
// 静的プロパティ呼び出し
console.log(Person.Pi); // 3.14
// メソッド呼び出し
console.log(p.show()); // "mido(30): mail"
// 静的メソッド呼び出し
console.log(Person.circle(10)); // 314
// セッター
p.age = 30;
// ゲッター
console.log(p.age); // 30
```

## 継承

クラスを継承するには `class クラス名 extends 親クラス名` を利用します。  
親のコンストラクタを呼び出すには `super(arg1, arg2, ...)` を利用します。  
親のメソッドを呼び出すには `super.メソッド名(arg1, ...)` を利用します。  

※ クラスの継承は一つまでです。複数のクラスを継承することはできません。

```typescript
class Person {
    constructor(protected name: string, protected age: number) {
    }
    public show(): string {
        return `${this.name}(${this.age})`;
    }
}
class BusinessPerson extends Person {
    protected clazz: string;
    // コンストラクタのオーバーライド
    constructor(name: string, age: number, clazz: string) {
        super(name, age); // 親のコンストラクタを呼び出す
        this.clazz = clazz;
    }
    // メソッドのオーバーライド
    public show(): string {
        return super.show() + `: ${this.clazz}`;
    }

    // メソッド定義
	public work(): string {
		return `${this.name} is working`;
    }
}

let p = new Person("mido", 28);
console.log(p.show()); // mido(28)

let bp = new BusinessPerson("kane", 28, "ymz");
console.log(bp.show()); // kane(28): ymz
console.log(bp.work()); // kane is working
```

## 抽象クラス

抽象クラスの宣言は `abstract class Figure { ... }` を利用します。  
抽象メソッドの宣言は `abstract メソッド名(arg, ...): 型 { ... }` を利用します。  
抽象メソッドは派生クラスでオーバーライド **しなければなりません** 。  

```typescript
abstract class Figure {
    constructor(protected width: number, protected height: number) {}

    // 抽象メソッド(実装クラスでオーバーライド必須)
    public abstract getArea(): number;

    // デフォルトメソッド
    public getElem(): string {
        return `w: ${this.width}, h: ${this.height}`;
    }
}

class Triangle extends Figure {
    public getArea(): number{
        return this.width * this.height / 2;
    }
}

let t = new Triangle(10, 5);
console.log(t.getElem()); // w: 10, h: 5
console.log(t.getArea()); // 25
```

## インターフェース

クラスの **ふるまい** を定義する仕組みです。

インターフェイスの定義は `interface インターフェイス名 { ... }` を利用します。  
インターフェイスを実装するには `class クラス名 implements インターフェイス名1, インターフェイス名2, ... { ... }` を利用します。  
※ インターフェイスで定義したメソッドは、派生クラスで必ず実装 **されなければなりません** 。  

```typescript
interface Hoge {
    // アクセス修飾子は指定できない(すべてpublic), デフォルトメソッドも定義できない
    app: string; // プロパティシグニチャ
    hoge(): string; // メソッドシグニチャ
}
interface Fuga {
    fuga(): string;
}
// interface から interfaceを継承するには extends を使う
interface Piyo extends Hoge {
    piyo(): string;

}

// interfaceを実装するにはimplementsを使う
class MyApp implements Hoge, Fuga, Piyo {
    public app: string = "app";
    public hoge(): string {
        return "hoge";
    }
    public fuga(): string {
        return "fuga";
    }
    public piyo(): string {
        return "piyo";
    }
}

let ma: Hoge & Fuga & Piyo = new MyApp();
console.log(ma.hoge()); // hoge
console.log(ma.fuga()); // fuga
console.log(ma.piyo()); // piyo
```

## メソッドチェイン

TypeScriptでは、 クラスのメソッド内で `this` を現在のインスタンス型として扱うことができ、戻り値にthis型を指定することでメソッドチェインを実装することができます。


```ts
class MyClass {
    constructor(private _value: number) {}
    
    get value(): number { return this._value; }
    
    plus(value: number): this {
        this._value += value;
        return this;
    }
    
    minus(value: number): this {
        this._value -= value;
        return this
    }
}

let c = new MyClass(10);
console.log(c.plus(10).minus(5).value);  // 15
```

# ■ ジェネリック型

参考
- [サバイバルTypeScript - ジェネリクス](https://typescriptbook.jp/reference/generics)

汎用的なクラス、メソッドを作るために、利用時に特定の型を指定することができる仕組みです。(つまり型のパラメータ化です)


```typescript
class MyApp<T> {
    constructor(private name: T) {}
    getName(): T {
        return this.name;
    }
}

let app = new MyApp<string>("ktamido");
let n: string = app.getName();
console.log(n); // ktamido
```

複数指定することも可能です。

```typescript
class Product<T, R> {
    constructor(private name: T, private price: R) {}
    getName(): T {
        return this.name;
    }
    getPrice(): R {
        return this.price;
    }
}

let product = new Product<string, number>("orange", 200);
let n: string = product.getName();
console.log(n); // orange

let p: number = product.getPrice();
console.log(p); // 200
```

`<T = string>` のようにデフォルト値を指定することもできます。

```ts
class MyGenerics<T = string> {
    value: T | null = null;
}

let g = new MyGenerics();
g.value = "hoge";
```


**型境界** を利用して渡すべき型を制限することも可能です。  
※ `<T extends Hhoge>` というような指定をすると `T` 型には `Hoge` 型の派生クラスを指定しなければなりません。


```ts
class MyApp<T extends Date> {
    constructor(private date: T) {}
    show(): string {
        return "now: " + this.date.toLocaleDateString();
    }
}

let app = new MyApp<Date>(new Date());
let date: string = app.show();
console.log(date); // now: 2019/8/3
```

## メソッド

メソッドの引数、戻り値、ローカル変数の型を、メソッドを呼び出す際に決めることができます。

```ts
class MyApp {
    public static addAll<T>(data: T[], ...values: T[]): T[] {
        return data.concat(values);
    }
}
let x = [10, 15, 30];
let ret = MyApp.addAll<number>(x, 35, 50);
console.log(ret); // [10, 15, 30, 35, 50]
```

## 関数



```ts
// function命令
function addAll1<T>(data: T[], ...values: T[]): T[] {
  return data.concat(values);
}

// 関数リテラル
const addAll2 = function<T>(data: T[], ...values: T[]): T[] {
  return data.concat(values);
}


// アロー関数
// <T> ではなく <T,> なので注意
const addAll3 = <T,>(data: T[], ...values: T[]): T[] => {
  return data.concat(values);
}

let x = [10, 15, 30];
console.log(addAll1<number>(x, 35, 50)); // [10, 15, 30, 35, 50]
console.log(addAll2<number>(x, 35, 50)); // [10, 15, 30, 35, 50]
console.log(addAll3<number>(x, 35, 50)); // [10, 15, 30, 35, 50]
```

# ■ モジュール

参考
- [サバイバルTypeScript](https://typescriptbook.jp/reference/modules)

モジュールはプログラムを複数ファイルに分割し、関連付けて、一つのプログラムとして動かす仕組みです。

※ この項の作業は最初に立てた開発shell内で行ってください。

```bash
# 最初に作成したTypeScriptのプロジェクトに移動
cd /opt/app/static/ts_tutorial

mkdir -p src/lib

# モジュールファイルの作成
touch src/lib/module.ts

# モジュールを利用するファイルを作成
touch src/app.ts
```

モジュールファイルを実装してみましょう。
`export` に注目してください。モジュールのメンバーは非公開がデフォルトなので、外部から利用したい関数やクラス、変数には `export` キーワードを付与します。

```ts
// --- static/ts_tutorial/src/lib/module.ts ---
const TITLE: string = 'TypeScript入門';

export function showMessage(): void {
    console.log(`ようこそ ${TITLE}`);
}

export class Util {
    static getVersion(): string { return "1.0.0"; }
}
```

`app.ts` からモジュールを利用してみましょう

```ts
// --- static/ts_tutorial/src/app.ts ---
import { showMessage, Util } from './lib/module'

showMessage();
console.log(Util.getVersion());
```


ビルドして実行してみましょう  

```bash
# src/app.ts と src/lib/module.ts をビルド
npx tsc src/app.ts src/lib/*.ts --outDir dist

# 実行
node dist/app.js
```

# ■ ビルド

## tsconfig.jsonを利用する

これまでは `tsc` コマンドを利用して、引数やオプションでビルド対象のファイルや出力先などを指定してきましたが、毎回ビルド時に細かいオプションを指定するのは手間なので、 `tsconfig.json` を利用してTypeScriptのビルド設定を定義しましょう。  
`tsconfig.json` にはビルド先のディレクトリや、トランスパイル後のJavaScriptのバージョン、どんなファイルをビルドに含めるかといった設定を記述します。

```
※ JavaScriptのバージョン
TypeScriptはJavaScriptにトランスパイルすることで、node.jsやブラウザから実行できますが、JavaScriptにもバージョンが存在します。  
ブラウザによって対応状況が異なるので、どのバージョンのJavaScriptにトランスパイルするかといった設定が必要になります。  

ちなみに、JavaScriptの標準仕様は ECMAScript という名前で定められており、下記のようなバージョンが存在します。  
ECMAScript: https://www.w3schools.com/js/js_versions.asp

es5, es6(es2015), es2016, es2017, es2018, es2019, es2020, es2021
```

```bash
# 最初に作成したTypeScriptのプロジェクトに移動
cd /opt/app/static/ts_tutorial

# tsconfig.jsonを生成
npx tsc --init
```

tsconfig.jsonの設定の参考

- [Intro to the TSConfig Reference](https://www.typescriptlang.org/tsconfig)
- [サバイバルTypeScript - tsconfig.jsonを設定する](https://typescriptbook.jp/reference/tsconfig/tsconfig.json-settings#%E5%88%9D%E3%82%81%E3%81%A6%E3%81%AEtsconfigjson)
- [tsconfig.jsonのよく使いそうなオプションを理解する](https://zenn.dev/chida/articles/bdbcd59c90e2e1)
- [【TypeScript】tsconfig.jsonの設定](https://qiita.com/crml1206/items/8fbfbecc0b40968bfc42)


```json
/* --- static/ts_tutorial/tsconfig.json --- */
{
  // コンパイルオプション
  "compilerOptions": {
    // https://www.typescriptlang.org/tsconfig#target
    // 出力するJavaScriptのバージョン
    "target": "es2021",
    // https://www.typescriptlang.org/tsconfig#lib
    // ブラウザ上で動かすなら dom を指定して、window, document といった型情報を取り込む
    "lib": ["es2021", "dom"],
    // https://www.typescriptlang.org/tsconfig#module
    // モジュールのインポート形式
    // - サーバーで動かす場合: commonjs
    // - ブラウザで動かす場合: es2015, es2020, es2022, esnext
    "module": "commonjs",
    // trueだと、デバッガがビルド前のソースファイルを表示できるようになる
    "sourceMap": true,
    // ビルド先のディレクトリ
    "outDir": "./dist",
    // ビルド対象のディレクトリ
    "rootDir": "./src",
    // https://www.typescriptlang.org/tsconfig#strict
    // trueにすると厳密な型チェックを行う
    "strict": true,
    // 相対モジュール名を解決するためのベースディレクトリ
    "baseUrl": "src",
    // コンパイル対象にJavaScriptファイルを含める
    "allowJs": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
  },
  // コンパイル対象のファイルを定義
  // 拡張子を指定していない場合は .ts, .tsx, .d.ts が含まれる
  // compilerOptions.allowJs = true なら .js, .jsx も含む
  "include": ["src/**/*"],
}
```

ビルド・実行してみましょう

```bash
# ビルド
# ビルドの設定はtsconfig.jsonを参照するため、引数を指定する必要はない
npx tsc

# 確認
ls dist/

# 実行
node dist/app.js
```

## webpackの設定

参考
- [webpack - GettingStarted](https://webpack.js.org/guides/getting-started/)
- [webpack - TypeScript](https://webpack.js.org/guides/typescript/)


`tsconfig.json` を利用することで、ビルドコマンドはだいぶシンプルになりましたが、 `tsc` を利用したビルド方法では、tsファイルに対応するjsファイルが複数生成されてしまいます。  
サーバーで動かすのであれば問題ありませんが、ブラウザで動かそうとすると依存ファイルをすべて読み込まなければならず、現実的ではありません。  
webpackを利用すると、ビルド後のファイルを1ファイルにまとめる(バンドル)ことができるため、ブラウザ側で簡単に読み込むことができるようになります。



```bash
# 最初に作成したTypeScriptのプロジェクトに移動
cd /opt/app/static/ts_tutorial

# webpackとwebpackでTypeScriptを解釈するためのts-loaderをインストールします。
npm install webpack-cli ts-loader --save-dev
```

webpackの設定を定義する `webpack.config.js` を作成します。

```js
// --- static/ts_tutorial/webpack.config.js ---
const path = require('path');

module.exports = {
  // エントリーポイント
  entry: './src/app.ts',
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  output: {
    // 出力ファイル名
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
  },
};
```

ビルドを実行しましょう


```bash
# ビルド実行
npx webpack

# 確認
ls dist/bundle.js

# サーバーサイドで実行
node dist/bundle.js
```

bundle.jsをhtmlから読み込んでみましょう

```html
<!-- --- static/index.html --- -->
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<body>
  <h1>Hello World</h1>

  <!-- hello.ts -->
  <script src="/ts_tutorial/tmp/hello.js"></script>
  <script>
    let v = add(100, 200)
    console.log("v: ", v)
  </script>
  <!-- hello.ts -->

  <!--bundle.js -->
  <script src="/ts_tutorial/dist/bundle.js"></script>
  <!--bundle.js -->

</body>
</html>
```

http://localhost:8018/ にアクセスしてみましょう
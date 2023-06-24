[Chapter8] 番外編2: TypeScriptのおさらい
--
[top](../../README.md)

# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter8/src` をルートディレクトリとして解説します。

Chapter8では、TypeScriptに触れていきましょう。  
最終的にフロントエンドはNuxt.jsを利用して実装する予定ですが、そもそもTypeScriptに触れたことがないと説明が難しいのでここで簡単に説明したいと思います。

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
npx tsc hello.ts --outDir dist

# ビルドを行うと dist/hello.js が生成されます。
cat dist/hello.js

# 実行
node dist/hello.js
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
  <script src="/ts_tutorial/dist/hello.js"></script>
  <script>
    let v = add(100, 200)
    console.log("v: ", v)
  </script>
</body>
</html>
```

http://localhost:8018/ にブラウザでアクセス

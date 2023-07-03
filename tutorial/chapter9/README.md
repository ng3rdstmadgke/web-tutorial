[Chapter9] Nuxt.js入門
--
[top](../../README.md)

# Note

このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter9/src` をルートディレクトリとして解説します。

chapter9では、Nuxtのプロジェクト作成から単純な画面の作成を行っていきます。

本チュートリアルではUIコンポーネントフレームワークとしてVuetifyを利用します。  
Vuetifyは公式がPlayGroundを用意していますので、挙動を確かめたいときに利用するとよいでしょう。  

[Vuetify Play | Vuetify](https://play.vuetifyjs.com/)


# ■ 前提

このチュートリアルを開始する前に、Vue.jsのチュートリアルを完了させてください

- [Vue.js チュートリアル](https://ja.vuejs.org/tutorial/#step-1)

# ■ Nuxt3プロジェクトの作成

```bash
# 開発用shellを起動
./bin/run.sh chapter9 --mode shell

# Nuxt3のプロジェクトを作成
mkdir front
cd front
npx nuxi init .

# Nuxt3内で利用されている各種パッケージをインストール
npm install

# 一度Nuxt3を起動してみましょう
npm run dev
```

ブラウザから http://localhost:3000/ にアクセスしてみましょう

```bash
# ctrl + c でサーバーを終了させて開発shellからログアウトします。
exit
```

# ■ アプリの起動

Nuxtサーバーは run.sh からも起動可能なので、APIサーバーと合わせて起動してみましょう

```bash
# ※ 起動していない場合のみ
./bin/mysql.sh

# 開発用shellを起動
./bin/run.sh chapter9 --mode shell

# データベースの初期化
./bin/init-database.sh

exit

# APIサーバーとNuxtサーバーを起動
./bin/run.sh chapter9 --mode app
```

ブラウザから NuxtサーバーとAPIサーバーにアクセスしてみましょう。

- Nuxtサーバー: http://localhost:3000/
- APIサーバー: http://localhost:8018/docs


# ■ nuxtのディレクトリ構造

プロジェクトに必要な ディレクトリを作成しておきます。

- [Nuxt Directory Structure | Nuxt3](https://nuxt.com/docs/guide/directory-structure/nuxt)
  - [assets/](https://nuxt.com/docs/guide/directory-structure/assets)
  - [components/](https://nuxt.com/docs/guide/directory-structure/components)
  - [composables/](https://nuxt.com/docs/guide/directory-structure/composables)
  - [layouts/](https://nuxt.com/docs/guide/directory-structure/layouts)
  - [middleware/](https://nuxt.com/docs/guide/directory-structure/middleware)
  - [modules/](https://nuxt.com/docs/guide/directory-structure/modules)
  - [pages/](https://nuxt.com/docs/guide/directory-structure/pages)
  - [plugins/](https://nuxt.com/docs/guide/directory-structure/plugins)
  - [utils/](https://nuxt.com/docs/guide/directory-structure/utils)
  - [nuxt.config.ts](https://nuxt.com/docs/guide/directory-structure/nuxt.config)


```bash
# 開発用shellを起動
./bin/run.sh chapter9 --mode shell

# ディレクトリ作成
cd front
mkdir -p assets components composables layouts middleware modules pages plugins utils
```


# ■ Vuetify3のセットアップ

- [Get started with GVuetify3 | Vuetify](https://vuetifyjs.com/en/getting-started/installation/)

Vuetifyはvueで利用できるuiコンポーネントフレームワークです。ここでは、Vuetifyのインストールとセットアップを行います。


## Vuetifyのインストール

```bash
# vuetify
#   - Vue.jsベースのUIコンポーネントフレームワーク
# sass
#   - CSSの拡張言語
#   - vueファイル内で <style lang="scss"> を利用するために必要
npm install -D vuetify sass
```

## Vuetifyのビルド設定

- [Nuxt Configuration Reference | Nuxt](https://nuxt.com/docs/api/configuration/nuxt-config)

vuetifyをnuxtのプロジェクトと一緒にトランスパイルするための設定を nuxt.config.ts に追加します。  
※ トランスパイルはBabelで行われます。


```ts
// --- front/nuxt.config.ts ---

import { defineNuxtConfig } from 'nuxt/config'
import vuetify from 'vite-plugin-vuetify'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  build: {
    // ビルド時にトランスパイルしたいライブラリを指定
    // build.transpile: https://nuxt.com/docs/api/configuration/nuxt-config#transpile
    transpile: ['vuetify'],
  },
})
```

NuxtでVuetifyを利用できるように、VuetifyのインスタンスをnuxtAppに追加するプラグインを作成します。

```bash
touch plugins/vuetify.ts
```

```ts
// --- front/plugins/vuetify.ts ---

import { createVuetify } from 'vuetify'

export default defineNuxtPlugin(nuxtApp => {
  // createVuetifyメソッドでVuetifyインスタンスを作成し、Nuxt.jsの vueApp に登録します。
  const vuetify = createVuetify({
    ssr: true,  // Vue3はssrが利用されているかを自動的に検出できないので、明示的にssrの利用有無を設定する
  })

  // Vue.js で Vuetify を使用する
  nuxtApp.vueApp.use(vuetify)
})
```

## VuetifyのCSSを利用できるように設定

Vuetifyに定義されているCSSをグローバルに設定することで、Nuxtのテンプレートから参照できるようにします。

```bash
touch assets/main.scss
```

```scss
/* --- front/assets/main.scss --- */
@use "vuetify/styles";
```

```ts
// --- front/nuxt.config.ts ---

// ... 略 ...
export default defineNuxtConfig({
  // ... 略 ...

  css: ['@/assets/main.scss'],
})
```


## Treeshakingの設定

- [Treeshaking | Vuetify](https://vuetifyjs.com/en/features/treeshaking/)

Treeshakingとは、実際に利用するコンポーネントのみをバンドルすることで、ビルドサイズを小さくできる仕組みです。


```bash
# vite-plugin-vuetify: https://www.npmjs.com/package/webpack-plugin-vuetify
npm install -D vite-plugin-vuetify
```

```ts
// --- front/nuxt.config.ts ---

// ... 略 ...
import vuetify from 'vite-plugin-vuetify'

export default defineNuxtConfig({
  // ... 略 ...

  modules: [
    // vite-plugin-vuetifyで必要なvuetifyのコンポーネントのみをバンドルするための設定
    async (options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig', (config) => {
        config.plugins!.push(vuetify())
      })
    },
  ],
  // viteの設定: https://ja.vitejs.dev/config/
  vite: {
    ssr: {  // SSRオプション: https://ja.vitejs.dev/config/ssr-options.html
      // 指定した依存関係が SSR のために外部化されるのを防ぎます。
      noExternal: ['vuetify'],
    },
    define: {  // define: https://ja.vitejs.dev/config/shared-options.html#define
      // グローバル定数の定義
      'process.env.DEBUG': false,
    },
  },
})
```

## アイコンフォント(mdi) の設定

- [Material Design Icons - JS SVG | Vuetify](https://vuetifyjs.com/en/features/icon-fonts/#material-design-icons-js-svg)
- [Material Design Icons | Pictogrammers](https://pictogrammers.com/library/mdi/)

mdiはすべて読み込むとデータサイズが大きいので、利用したもののみバンドルするように設定します。


```bash
npm install -D @mdi/js
```

```ts
// --- front/plugins/vuetify.ts ---

// ... 略 ...
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg';  // 追加

export default defineNuxtPlugin(nuxtApp => {
  const vuetify = createVuetify({
    // ... 略 ...
    icons: {  // アイコンの設定
        defaultSet: 'mdi',
        aliases,
        sets: {
            mdi,
        },
    },
  })
  // ... 略 ...
})
```

下記のようにアイコンを利用できます。

```vue
<!-- *** front/app.vue *** -->

<template>
  <div>
    <div>
        アイコン: <v-icon :icon="mdiAccount" />
    </div>
    <NuxtWelcome />
  </div>
</template>

<script setup lang="ts">
import { mdiAccount } from '@mdi/js'
</script>
```


## テーマの設定

VuetifyのUIコンポーネントに適用されるテーマカラーを設定していきます。

- [Theme | Vuetify](https://vuetifyjs.com/en/features/theme/)


```ts
// --- front/plugins/vuetify.ts ---

import { createVuetify, ThemeDefinition } from 'vuetify'   // 変更
// ... 略 ...

// カスタムテーマを定義
const myCustomLightTheme: ThemeDefinition = {
  dark: false,
  colors: {
      primary: "#1F2D5A",
      secondary: "#38508a",
      accent: "#FB8C00",
      success: "#43A047",
      info: "#0288D1",
      warning: "#FFC107",
      error: "#F44336",
  },
}


export default defineNuxtPlugin(nuxtApp => {
  const vuetify = createVuetify({
    // ... 略 ...
    theme: {
      defaultTheme: "myCustomLightTheme",
      themes: {
        myCustomLightTheme,
      }
    },
  })
  // ... 略 ...
})

```

# ■ アプリ実装

さて、これらの設定が一通り終わったらサンプルページを実装してみましょう。  
ページは共通レイアウト (ヘッダー、フッター、メニューなどどのページでも共通して利用される部分) とコンテンツに分かれています。  

- 共通レイアウトは `layouts/` ディレクトリ配下に実装し、 `NuxtLayout` タグで参照します。  
[\<NuxtLayout> | Nuxt](https://nuxt.com/docs/api/components/nuxt-layout#nuxtlayout)
- コンテンツは `pages/` ディレクトリ配下に実装し、 `NuxtPage` タグで参照します。  
[\<NuxtPage> | Nuxt](https://nuxt.com/docs/api/components/nuxt-page)

```vue
<!-- front/app.vue -->

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
```

## 共通レイアウトの実装

- [Layouts | Nuxt](https://nuxt.com/docs/migration/pages-and-layouts#layouts)
- [ワイヤーフレームのサンプル | Vuetify](https://vuetifyjs.com/en/getting-started/wireframes/)

共通レイアウトは `layouts/default.vue` に実装します。  
`default.vue` というファイル名は、 `NuxtLayout` タグでデフォルトで読み込まれるファイルとなります。


```bash
touch layouts/default.vue
```

- 利用するVuetifyのコンポーネント
  - [v-app-bar - App bars (ヘッダー) | Vuetify](https://vuetifyjs.com/en/components/app-bars/)
  - [v-navigation-drawer - Navigation drawers (サイドメニュー) | Vuetify](https://vuetifyjs.com/en/components/navigation-drawers/)
  - [v-footer - Footers (フッター) | Vuetify](https://vuetifyjs.com/en/components/footers/)
  - [v-list - List (リスト) | Vuetify](https://vuetifyjs.com/en/components/lists/)
  - [v-btn - Buttons (ボタン) | Vuetify](https://vuetifyjs.com/en/components/buttons/)
  - [v-icon - Icons (アイコン) | Vuetify](https://vuetifyjs.com/en/components/icons/)
  - [v-sheet - Sheets (枠) | Vuetify](https://vuetifyjs.com/en/components/sheets/)

```vue
<!-- front/layouts/default.vue -->
<template>
  <v-app id="inspire">
    <!-- ヘッダー >>> -->
    <v-app-bar color="primary" :elevation="2">
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title>
        <div @click="useRouter().push('/')" style="cursor: pointer;">SampleApp</div>
      </v-app-bar-title>
      <v-btn :icon="mdiLogout"></v-btn>
    </v-app-bar>
    <!-- <<< ヘッダー -->

    <!-- サイドメニュー >>> -->
    <v-navigation-drawer v-model="drawer">
      <!-- プロフィール -->
      <v-sheet color="grey-lighten-4" class="pa-4" >
        <v-avatar class="mb-4" color="accent" size="64" >SA</v-avatar>
        <div>sample.app</div>
      </v-sheet>
      <!-- プロフィール -->
      <v-divider></v-divider>
      <!-- メニューリスト >>> -->
      <v-list>
        <template v-for="item in menu" :key="item.name" >
          <v-list-item link :to="item.path">
            <template v-slot:prepend>
              <v-icon>{{ item.icon }}</v-icon>
            </template>
            <v-list-item-title>{{ item.name }}</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>
      <!-- メニューリスト >>> -->
    </v-navigation-drawer>
    <!-- <<< サイドメニュー -->

    <!-- コンテンツ >>> -->
    <v-main>
      <v-container class="py-8 px-6" fluid >
        <slot />
      </v-container>
    </v-main>
    <!-- <<< コンテンツ -->

    <!-- フッター >>> -->
    <v-footer class="footer justify-center">
      <div>&copy; 2023 Nuxt tutorial</div>
    </v-footer>
    <!-- <<< フッター -->
  </v-app>
</template>

<script setup lang="ts">
import { mdiAccount, mdiNote, mdiLogout, mdiLogin, mdiInformation } from '@mdi/js'

interface MenuItem {
  icon: string
  name: string
  path: string
}

const drawer = ref<boolean>(false)
const menu = ref<Array<MenuItem>>([
  {
    icon: mdiLogin,
    name: "Login",
    path: "/login",
  },
  {
    icon: mdiNote,
    name: "Item",
    path: "/items/",
  },
  {
    icon: mdiAccount,
    name: "User",
    path: "/users/",
  },
])
</script>

<style lang="scss">
.footer {
  width: 100%;
  position: absolute;
  bottom: 0;
}
</style>
```


## コンテンツの実装

- [Pages | Nuxt](https://nuxt.com/docs/migration/pages-and-layouts#pages)

コンテンツは `pages/` 配下に実装します。  
`pages/` 配下はURLのパス部分と一致するようにファイルを作成していきます。こうすることで、明示的にルーティング設定を行わずとも、対応するvueファイルに自動的にルーティングを行うことができます。

例えばこんな感じ

```
http://localhost:3000/ -> pages/index.vue
http://localhost:3000/items/create -> pages/items/create.vue
http://localhost:3000/items/1/edit -> pages/items/[itemId]/edit.vue
```


`http://localhost:3000/` にアクセスしたときに表示されるコンテンツを作成してみましょう。


```bash
touch pages/index.vue
```

- 利用するVuetifyのコンポーネント
  - [v-table - Tables (テーブル) | Vuetify](https://vuetifyjs.com/en/components/tables/)
  - [Flex (要素を横並びにする機能) | Vuetify](https://vuetifyjs.com/en/styles/flex/)
  - [v-btn - Buttons (ボタン) | Vuetify](https://vuetifyjs.com/en/components/buttons/)
  - [v-icon - Icons (アイコン) | Vuetify](https://vuetifyjs.com/en/components/icons/)

```vue
<!-- *** front/pages/index.vue *** -->

<template>
  <div>
    <div class="mb-3">
      <div class="text-h4">Items</div>
    </div>
    <v-table>
      <thead>
        <tr>
          <th>id</th>
          <th>title</th>
          <th>action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.title }}</td>
          <td>
            <div class="d-flex">
              <div>
                <v-btn icon flat >
                  <v-icon color="warning" :icon="mdiNoteEditOutline"></v-icon>
                </v-btn>
              </div>
              <div>
                <v-btn icon flat >
                  <v-icon color="error" :icon="mdiDeleteForeverOutline"></v-icon>
                </v-btn>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </v-table>
  </div>
</template>

<script setup lang="ts">
// refは明示的なインポートは不要だが、説明のために記述している
import { ref } from 'vue'
import { mdiNoteEditOutline, mdiDeleteForeverOutline } from '@mdi/js'

const items = ref<any>([
    {id: "1", "title": "Chapter1 FastAPI入門"},
    {id: "2", "title": "Chapter2 RDB入門"},
    {id: "3", "title": "Chapter2.5 SQLAlchemyを利用したデータベースの操作"},
    {id: "4", "title": "Chapter3 Alembicを利用したマイグレーションを実装してみよう"},
    {id: "5", "title": "Chapter4 FastAPIでCRUDを実装してみよう"},
])

</script>
```

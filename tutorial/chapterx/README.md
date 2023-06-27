[Chapterx] Nuxtプロジェクト
--
[top](../../README.md)


# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapterx/src` をルートディレクトリとして解説します。

参考
- https://codybontecou.com/how-to-use-vuetify-with-nuxt-3.html
- https://zenn.dev/coedo/articles/nuxt3-vuetify3
- https://qiita.com/ot_RikuOta/items/bd644957dacbac057a05

# ■ 前提

このチュートリアルを開始する前に、Vue.jsのチュートリアルを完了させてください

[Vue.js チュートリアル](https://ja.vuejs.org/tutorial/#step-1)


# ■ プロジェクト作成


```bash
# 開発用shellを起動
./bin/run.sh chapterx --mode shell
```

## Nuxt3プロジェクトの作成

```bash
# Nuxt3のプロジェクトを作成
mkdir front
cd front
npx nuxi init .

# Nuxt3内で利用されている各種パッケージをインストール
npx install


# 一度Nuxt3を起動してみましょう
# http://localhost:3000/ にアクセス
npm run dev
```

### nuxtのディレクトリ構造

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

ディレクトリを作成しておきます。

```bash
mkdir -p assets components composables layouts middleware modules pages plugins utils
```


## Vuetify3のセットアップ

Vuetifyはvueで利用できるuiコンポーネントフレームワークです。

```bash
# vuetify
#   - Vuetify3
#   - Vue.jsベースのUIコンポーネントフレームワーク
# sass
#   - CSSの拡張言語
#   - vueファイル内で <style lang="scss"> を利用するために必要
npm install -D vuetify sass
```

nuxt.config.ts設定

- [Nuxt Configuration Reference | Nuxt3](https://nuxt.com/docs/api/configuration/nuxt-config)

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

NuxtのプラグインでVuetifyを読み込み

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

### vuetifyに定義されているCSSを利用できるようにする

vuetifyに定義されているCSSをグローバルに設定することで、自身のテンプレートから参照できるようにします。

```scss
/* --- front/layouts/main.scss --- */
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


### Treeshakingの設定

Treeshakingとは、実際に利用するコンポーネントのみをバンドルすることで、ビルドサイズを小さくできる仕組みです。

- [Treeshaking | Vuetify](https://vuetifyjs.com/en/features/treeshaking/)

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
    async (options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig', config => config.plugins.push(
        vuetify()
      ))
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


### アイコンフォント(mdi) の設定

mdiはサイズが大きいので、利用したもののみバンドルするように設定します。

- [Material Design Icons - JS SVG | Vuetify](https://vuetifyjs.com/en/features/icon-fonts/#material-design-icons-js-svg)
- [Material Design Icons | Pictogrammers](https://pictogrammers.com/library/mdi/)


```bash
npm install -D @mdi/js
```

```ts
// --- front/plugins/vuetify.ts ---

// ... 略 ...
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg';

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
<!-- --- front/app.vue -->

<template>
  <div>
    <v-icon :icon="mdiAccount" />
  </div>
</template>

<script setup lang="ts">
import { mdiAccount } from '@mdi/js'
</script>
```

## テーマの設定

- [Theme | Vuetify](https://vuetifyjs.com/en/features/theme/)


```ts
// --- front/plugins/vuetify.ts ---

import { createVuetify, ThemeDefinition } from 'vuetify'   // 変更
// ... 略 ...

// カスタムテーマを定義
const myCustomLightTheme: ThemeDefinition = {
  dark: false,
  colors: {
      primary: "#673ab7",
      secondary: "#9c27b0",
      accent: "#009688",
      error: "#ff5722",
      warning: "#ffc107",
      info: "#2196f3",
      success: "#4caf50",
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
    }
  })
  // ... 略 ...
})

```

# ■ アプリ実装

`NuxtLayout` タグは `layouts` ディレクトリ、 `NuxtPage` タグは `pages` ディレクトリのファイルを指します。  
`default.vue` というファイル名は、これらのタグでデフォルトで読み込まれるファイルとなります。

```vue
<!-- front/app.vue -->

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
```

## 共通レイアウトの作成

- [ワイヤーフレームのサンプル | Vuetify](https://vuetifyjs.com/en/getting-started/wireframes/)

```bash
touch front/layouts/default.vue
```

```vue
<!-- front/layouts/default.vue -->
<template>
  <v-app id="inspire">
    <v-app-bar color="primary" :elevation="2">
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title>SampleApp</v-app-bar-title>
      <v-btn :icon="mdiLogout"></v-btn>
    </v-app-bar>
    <v-navigation-drawer v-model="drawer">
      <v-sheet color="grey-lighten-4" class="pa-4" >
        <v-avatar class="mb-4" color="accent" size="64" >John</v-avatar>
        <div>keita.midorikawa</div>
      </v-sheet>

      <v-divider></v-divider>

      <v-list>
        <v-list-item v-for="[icon, text] in links" :key="icon" link >
          <template v-slot:prepend>
            <v-icon>{{ icon }}</v-icon>
          </template>
          <v-list-item-title>{{ text }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <v-container class="py-8 px-6" fluid >
        <slot />
      </v-container>
    </v-main>
    <v-footer>
      <span>&copy; 2021</span>
    </v-footer>
  </v-app>
</template>

<script setup lang="ts">
import { mdiAccount, mdiNote, mdiLogout } from '@mdi/js'

const drawer = ref<boolean>(true)
const links = ref<Array<[any, string]>>([
  [mdiNote, 'Item'],
  [mdiAccount, 'User'],
])
</script>
```

# ■ メモ

## serverとclientの判定

```
process.client
```

## カスタムコンポーネント

```
defineEmits, defineProps, defineExpose
```


## 画面遷移

```ts
useRouter().push({path: "/"})
```

## $fetch

- $fetch: https://nuxt.com/docs/api/utils/dollarfetch#fetch
- ofetch: https://github.com/unjs/ofetch

Nuxtは `ofetch` を `$fetch` としてグローバルに公開している.

## useRuntimeConfig

コンフィグの定義

```ts
/* --- nuxt.config.ts --- */

export default defineNuxtConfig({
  runtimeConfig: {
    // Private keys are only available on the server
    apiSecret: '123',

    // Public keys that are exposed to the client
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '/api'
    }
  }
})
```

使い方

```ts
<script setup lang="ts">
const config = useRuntimeConfig()
</script>
```

## apiコンポーザブル

```ts
/* --- nuxt.config.ts --- */
export default defineNuxtConfig({
  // 実行時参照したいグローバルな変数を定義
  runtimeConfig: {
    // public配下はサーバーとクライアント両方で使える
    public: {
      clientBaseUrl: process.env.NUXT_CLIENT_BASE_URL || '//localhost:8018/api/v1',
      serverBaseUrl: process.env.NUXT_SERVER_BASE_URL || 'http://localhost:8018/api/v1',
    }
  }
})
```

## バリデーション

https://vuetifyjs.com/en/components/forms/#exposed-properties

```vue
<template>
  <v-form ref="form" @submit.prevent="submit">
    <v-text-field
      v-model="title"
      label="title"
      :rules="[ required ]"
      ></v-text-field>
    <v-btn color="primary" type="submit" >作成</v-btn>
  </v-form>
</template>


<script setup lang="ts">

const title = ref<string>("")

const form = ref<any>(null)   // v-formのref

function required(v: string) boolean | string {
  return !!v || 'title is required'
}

async function submit(event: Event) {
  // バリデーション実行
  const {valid, errors} = await form.value.validate()
  // バリデーションの表示をリセットしたいときは form.value.resetValidation()
  // 入力値とバリデーション表示両方をリセットしたいときは form.value.reset()
  if (!valid) {
    return
  }
  // ... APIリクエスト ...
}
</script>
```
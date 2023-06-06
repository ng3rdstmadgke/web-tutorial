[Chapterx] Nuxtプロジェクト
--
[top](../../README.md)

# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapterx/src` をルートディレクトリとして解説します。

参考
- https://codybontecou.com/how-to-use-vuetify-with-nuxt-3.html
- https://zenn.dev/coedo/articles/nuxt3-vuetify3
- https://qiita.com/ot_RikuOta/items/bd644957dacbac057a05

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
# vite-plugin-vuetify
#   - Vuetifyコンポーネントの自動インポートを行う
#   - トランスパイル後のバンドルサイズを小さくする
# @mdi/js
#   - アイコンフォント
npm install -D vuetify sass vite-plugin-vuetify
```

### NuxtのプラグインでVuetifyを読み込む

```ts
// --- front/plugins/vuetify.ts ---
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'  // Vuetifyのすべてのコンポーネントを読み込む
import * as directives from 'vuetify/directives'  // Vuetifyのすべてのディレクティブを読み込む

export default defineNuxtPlugin(nuxtApp => {
  /**
   * createVuetifyメソッドでVuetifyインスタンスを作成し、Nuxt.jsの vueApp に登録します。
   * componentsとdirectivesを含めることで、Nuxt.jsアプリ内でVuetifyのコンポーネントとディレクティブが使用可能になります。
   */
  const vuetify = createVuetify({
    ssr: true,  // Vue3はssrが利用されているかを自動的に検出できないので、明示的にssrの利用有無を設定する
    // 各種設定の読み込み
    components,  // すべてのコンポーネントをincludeする
    directives,  // すべてのディレクティブをincludeする
  })

  // Vue.js で Vuetify を使用する
  nuxtApp.vueApp.use(vuetify)
})
```



## nuxt.config.ts設定

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
  // Nuxtイベントのリスナー
  hooks: {
    'vite:extendConfig': (config) => {
      config.plugins!.push(vuetify())
    },
  },
  // グローバルに設定したいCSSファイル・モジュールをセット
  // css: https://nuxt.com/docs/api/configuration/nuxt-config#css
  css: [
    'vuetify/styles',  // vuetifyのCSSをグローバルにセット
  ],
  vite: {
    ssr: {
      noExternal: ['vuetify'],
    },
    define: {
      'process.env.DEBUG': false,
    },
  },
})
```

## アイコンフォント(mdi) の導入

mdiはサイズが大きいので、利用したもののみバンドルするように設定します。

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

下記のような語りで利用できるようになります。

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

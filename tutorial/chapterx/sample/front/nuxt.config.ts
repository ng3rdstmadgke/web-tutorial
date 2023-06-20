import { defineNuxtConfig } from 'nuxt/config'
import vuetify from 'vite-plugin-vuetify'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  build: {
    // ビルド時にトランスパイルしたいライブラリを指定
    // build.transpile: https://nuxt.com/docs/api/configuration/nuxt-config#transpile
    transpile: ['vuetify'],
  },
  css: ['@/assets/main.scss'],
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
  // 実行時参照したいグローバルな変数を定義
  runtimeConfig: {
    public: {
      // clientBaseUrl: process.env.NUXT_CLIENT_BASE_URL || '//localhost:8018/api/v1',
      // serverBaseUrl: process.env.NUXT_SERVER_BASE_URL || 'http://localhost:8018/api/v1',
      clientBaseUrl: '//localhost:8018/api/v1',
      serverBaseUrl: 'http://localhost:8018/api/v1',
    }

  }
})
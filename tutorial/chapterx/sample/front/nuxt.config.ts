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
    'vuetify/styles'
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
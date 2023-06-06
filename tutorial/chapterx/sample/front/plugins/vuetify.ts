import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg';

export default defineNuxtPlugin(nuxtApp => {
  // createVuetifyメソッドでVuetifyインスタンスを作成し、Nuxt.jsの vueApp に登録します。
  const vuetify = createVuetify({
    ssr: true,  // Vue3はssrが利用されているかを自動的に検出できないので、明示的にssrの利用有無を設定する
    icons: {  // アイコンの設定
        defaultSet: 'mdi',
        aliases,
        sets: {
            mdi,
        },
    },
  })
  // Vue.js で Vuetify を使用する
  nuxtApp.vueApp.use(vuetify)
})

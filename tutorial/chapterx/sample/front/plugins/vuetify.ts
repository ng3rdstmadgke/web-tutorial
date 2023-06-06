import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'  // Vuetifyのすべてのコンポーネントを読み込む
import * as directives from 'vuetify/directives'  // Vuetifyのすべてのディレクティブを読み込む
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg';

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

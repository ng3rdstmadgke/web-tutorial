[Chapter10] ログインページの実装
--
[top](../../README.md)

# Note

このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter10/src` をルートディレクトリとして解説します。

chapter10では、Nuxtでログインページを実装します。

# ■ アプリの起動

Nuxtサーバーは run.sh からも起動可能なので、APIサーバーと合わせて起動してみましょう

```bash
# ※ 起動していない場合のみ
./bin/mysql.sh

# 開発用shellを起動
./bin/run.sh chapter10 --mode shell

# データベースの初期化
./bin/init-database.sh

exit

# APIサーバーとNuxtサーバーを起動
./bin/run.sh chapter10 --mode app
```

ブラウザから NuxtサーバーとAPIサーバーにアクセスしてみましょう。

- Nuxtサーバー: http://localhost:3000/
- APIサーバー: http://localhost:8018/docs

```bash
# 開発用shellを起動
./bin/run.sh chapter10 --mode shell

# ディレクトリ作成
cd front
mkdir -p assets components composables layouts middleware modules pages plugins utils
```

# ■ 認証トークンを扱うユーティリティ

認証トークン(JWT)はフロントエンドではCookieで管理します。
今回実装するユーティリティは、認証トークンをCookieに保存したり、Cookieから読みだしたり、認証済みかどうかの判定したりする機能を提供します。  
※ Cookieはブラウザ上で小さなテキスト情報を保持できる仕組みです。

Nuxt では `utils/` 配下にユーティリティ関数を実装する決まりになっているため、 `utils/auth.ts` に認証ユーティリティを実装します。  
※ `utils/` 配下のモジュールは自動インポートの対象で、 様々な場所で明示的なインポート無しに利用できます。

 - [Directory Structure - utils/ | Nuxt](https://nuxt.com/docs/guide/directory-structure/utils)
   `utils/` ディレクトリの説明
 - [Directory Structure - composables - usage | Nuxt](https://nuxt.com/docs/guide/directory-structure/composables#usage)
   `utils/` `composables/` 配下の基本的な実装方法です。
 - [useCookie | Nuxt](https://nuxt.com/docs/api/composables/use-cookie#usecookie)  
   Cookieにアクセスするコンポーザブルです (SSRでも利用可能です)

```ts
// --- front/utils/auth.ts ---
import { Buffer } from 'buffer'

// Authクラスを返すuseAuthをエクスポートし外部から利用できるようにする
export const useAuth = () => {
  return Auth
}

interface tokenPayload {
  sub: string
  scopes: string[]
  exp: number
}

class Auth {
  // Cookieのキー
  private static ACCESS_TOKEN_KEY: string = "__access_token"

  // 認証済みかどうかの判定
  public static authenticated(): boolean {
    let payload = this.getPayload()
    if (payload) {
      // トークンの有効期限を検証
      let now  = Math.floor((new Date()).getTime() / 1000)
      return payload.exp > now
    }
    return false
  }

  // CookieからJWTを削除
  public static logout(): void {
    const cookie = useCookie(this.ACCESS_TOKEN_KEY)
    cookie.value = null
  }

  // JWTをCookieに保存
  public static login(token: string): void {
    const cookie = useCookie(this.ACCESS_TOKEN_KEY)
    cookie.value = token
  }

  // CookieからJWTを取得する
  public static getToken(): string | null {
    const cookie = useCookie(this.ACCESS_TOKEN_KEY);
    let token = cookie.value;
    return (token && Auth.authenticated()) ? token : null;
  }

  // Cookieに保存されているJWTのpayloadをオブジェクト形式で取得する
  public static getPayload(): tokenPayload | null {
    const cookie = useCookie(this.ACCESS_TOKEN_KEY)
    let token = cookie.value
    if (!token) return null
    let payload = token.split(".")[1]
    let decoded = Buffer.from(payload, "base64").toString()
    return JSON.parse(decoded)
  }

  // JWTのペイロードからユーザー名を取得する
  public static getUsername(): string | null {
    let payload = Auth.getPayload();
    return (payload && !!payload.sub) ? payload.sub : null
  }

  // JWTのペイロードのパーミッションに指定したパーミッションが含まれているかを判定する
  public static hasPermission(required_permissions: string[]): boolean {
    let required_permission_set = new Set(required_permissions)
    let payload = this.getPayload();
    let scopes: string[] = (payload) ? payload["scopes"] : []
    // 積集合
    let actual = new Set(scopes.filter(x => required_permission_set.has(x)))
    return actual.size == required_permission_set.size
  }
}
```

# ■ ログインが必要なページの実装

ログインが必要なページでは、ページの描画前にログインチェックをしなければなりません。  
Nuxtではmiddlewareという仕組みを利用することで、特定のルートに移動する前に任意のコードを実行することができます。  
この仕組みを利用して、ページ描画前に認証の有無を確認する処理を実装してみましょう。  

- [Middleware Directory | Nuxt](https://nuxt.com/docs/guide/directory-structure/middleware)


※ Nuxtは `navigateTo()` と `abortNavigation()` というmiddlewareのコールバック内でのみ利用可能な2つの関数を提供しています。

- `navigateTo (to: RouteLocationRaw | undefined | null, options?: { replace: boolean, redirectCode: number, external: boolean )`
  引数に渡したパスにリダイレクトします。
- `abortNavigation (err?: string | Error)`
  ナビゲーションを中止し、オプションのエラーメッセージを表示します。

```ts
// --- front/middleware/auth.ts ---

// ミドルウェアは現在のルートをあらわす to と、遷移元のルートをあらわす from を引数に取ります。
export default defineNuxtRouteMiddleware((to, from) => {
  // 先ほど実装した Auth.authenticated を利用してログイン確認
  const auth = useAuth()  // useAuthは utils/ に定義されているため自動インポートされる
  if (!auth.authenticated()) {
    // 認証されていない場合はログインページにリダイレクト
    return navigateTo('/login')
  }
})
```

`front/pages/index.vue` にmiddlewareを設定して、ログインが必要なページにしましょう。  
middlewareをページに設定するには `definePageMeta` を利用します。  

- [What Order Middleware Runs In | Nuxt](https://nuxt.com/docs/guide/directory-structure/middleware#what-order-middleware-runs-in)


```vue
<!-- *** front/pages/index.vue *** -->

<template>
  <!-- ... 略 ... -->
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ["auth"]  // middlewareの項目に auth.ts を指定
})

  // ... 略 ...
</script>
```

ついでに `front/pages/login.vue` にダミーの要素を作っておきましょう。

```vue
<!-- *** front/pages/login.vue *** -->
<template>
  <div>Login Page</div>
</template>
```

ブラウザで http://localhost:3000/ にアクセスしてみましょう。  
ログインしていないので http://localhost:3000/login にリダイレクトされるはずです。

# ■ ログインページの実装

APIからトークンの取得を行い、Cookieにトークンを保存するログイン画面を実装してみましょう。

## # useAsyncData

- [useAsyncData | Nuxt](https://nuxt.com/docs/api/composables/use-async-data)

NuxtでAPIにリクエストを送信するには `useAsyncData` を利用します。  
非同期でデータを取得するAPIなので、同期的に処理を記述したい場合は `await` を利用して実行します。

■ 引数
- key: `string`  
  このリクエストを一意に指定するキーを指定します。(APIへの重複アクセスを排除してくれる)
- handler: `(nuxtApp?: NuxtApp) => Promise<DataT>`  
  このハンドラーのなかでAPIへのリクエストを行います。
- options?: `AsyncDataOptions<DataT>`  
  - lazy (default: false)  
    クライアントサイドで呼ばれた際にデータフェッチの完了を待機せずにページ遷移を行う
  - default  
    データフェッチが完了するまでの間、戻り値のdataに設定する値を指定する。
  - server (default: true)  
    trueならサーバーサイドでデータフェッチを実行。falseならクライアントサイドでデータフェッチを実行。
  - transform  
    取得したデータの形式を変換するための関数を指定する

■ 戻り値
- data: `Ref<DataT | null>`  
  引数のhandlerの戻り値をrefでラップしたデータ。 初期値はref(null)
- pending: `Ref<boolean>`  
  データフェッチが完了するまではtrue、完了したらfalse
- refresh: `(opts?: AsyncDataExecuteOptions) => Promise<void>`  
  リクエストをもう一度実行するための関数
- error: `Ref<ErrorT | null>`  
  データフェッチに失敗した場合のエラーオブジェクト
- status: `'idle' | 'pending' | 'success' | 'error'`  
  データフェッチの現在の状態 (idle, pending, success, error)




## # ログインページ

- 利用するVuetifyのコンポーネント
  - [v-row,v-col - Grid system](https://vuetifyjs.com/en/components/grids/#grid-system)
  - [v-card - Cards (カード) | Vuetify](https://vuetifyjs.com/en/components/cards/)
  - [v-form - Form (フォーム) | Vuetify](https://vuetifyjs.com/en/components/forms/)
  - [v-text-field - Text fields (テキスト入力フォーム) | Vuetify](https://vuetifyjs.com/en/components/text-fields/)
  - [v-btn - Buttons (ボタン) | Vuetify](https://vuetifyjs.com/en/components/buttons/)
  - [v-icon - Icons (アイコン) | Vuetify](https://vuetifyjs.com/en/components/icons/)

```vue
<!-- *** front/pages/login.vue *** -->
<template>
<div>
  <div class="my-10">
    <v-row justify="center">
      <v-col cols="12" lg="4" sm="6">
      <v-card class="pa-5">
        <v-card-title class="d-flex justify-center mb-3">
          <div>
            <v-img :src="`/logo-no-background.png`" contain height="180"></v-img>
          </div>
        </v-card-title>
        <v-form ref="loginForm" lazy-validation>
          <v-text-field
            v-model="username"
            label="Username"
          ></v-text-field>
          <v-text-field
            v-model="password"
            label="Password"
            type="password"
          ></v-text-field>
          <div class="d-flex justify-end">
            <v-btn color="secondary" class="mr-4" type="submit" @click.prevent="submit">login</v-btn>
          </div>
        </v-form>
      </v-card>
      </v-col>
    </v-row>
  </div>
</div>
</template>

<script setup lang="ts">

// テキストフィールドにバインドされるデータ
const username = ref<string>("")
const password = ref<string>("")

interface LoginResponse {
  access_token: string
  token_type: string
}

// "LOGIN" ボタンがクリックされたときに呼び出される関数
async function submit() {
  const { data, pending, error, refresh } = await useAsyncData<LoginResponse>(
    "login",
    () => {
      let form = new FormData()
      form.append("username", username.value)
      form.append("password", password.value)
      return $fetch("//localhost:8018/api/v1/token", {
        method: "POST",
        headers: {},
        body: form,
      })
    }
  )
  // ログイン失敗ならログを出力してreturn
  if (!data.value || error.value) {
    console.error(error.value)
    return
  }
  // ログイン成功ならCookieにトークンをセット
  useAuth().login(data.value.access_token)
  // トップページにリダイレクト
  useRouter().push({ path: "/"})
}
</script>
```

# ■ ログアウト機能の実装

ヘッダー右端のログアウトボタンをクリックしてログアウトできるようにしましょう。

```vue
<!-- *** front/layouts/default.vue *** -->

<template>
    <!-- ... 略 ... -->

    <!-- ヘッダー >>> -->
    <v-app-bar color="primary" :elevation="2">
      <!-- ... 略 ... -->

      <!-- ログイン中だけ表示したいので v-ifで表示切替。クリック時に logout() を実行。 -->
      <v-btn v-if="auth.authenticated()" @click="logout()" :icon="mdiLogout"></v-btn>
    </v-app-bar>
    <!-- <<< ヘッダー -->

    <!-- ... 略 ... -->
</template>

<script setup lang="ts">

// ... 略 ...

const auth = useAuth()

function logout() {
  useAuth().logout()
  useRouter().push({path: "/login"})
}
</script>

<!-- ... 略 ... -->
```

# ■ メニューに表示される項目の切り替え

現在、メニューには `Login` `Item` `User` がログインの有無にかかわらず表示されていますが、未ログイン時は `Login` 、ログイン時は `Item` `User` を表示するようにします。


```vue
<!-- *** front/layouts/default.vue *** -->

<template>
    <!-- ... 略 ... -->

      <!-- メニューリスト >>> -->
      <v-list>
        <template v-for="item in menu" :key="item.name" >
          <!-- 追加: v-if="item.authenticated === auth.authenticated()" -->
          <v-list-item v-if="item.authenticated === auth.authenticated()" link :to="item.path">
            <template v-slot:prepend>
              <v-icon>{{ item.icon }}</v-icon>
            </template>
            <v-list-item-title>{{ item.name }}</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>
      <!-- メニューリスト >>> -->

    <!-- ... 略 ... -->
</template>

<script setup lang="ts">

// ... 略 ...

interface MenuItem {
  icon: string
  name: string
  path: string
  authenticated: boolean  // 追加
}

const drawer = ref<boolean>(false)
const menu = ref<Array<MenuItem>>([
  {
    icon: mdiLogin,
    name: "Login",
    path: "/login",
    authenticated: false,  // 追加
  },
  {
    icon: mdiNote,
    name: "Item",
    path: "/items/",
    authenticated: true,  // 追加
  },
  {
    icon: mdiAccount,
    name: "User",
    path: "/users/",
    authenticated: true,  // 追加
  },
])

// ... 略 ...
</script>

<!-- ... 略 ... -->
```

# ■ ログイン失敗時にアラートを表示

現状の実装だと、ログインに失敗してもウンともスンともいわないので、ユーザーにとって不親切なUIといえます。  
ログイン失敗時にアラートを表示することで、明示的に失敗をユーザーに知らせるようにしてみましょう。

アラート表示は他の画面でも同様に利用されることが想定されますので、再利用可能な形で実装したいところです。  
このような共通コンポーネントは、Nuxtでは `components/` ディレクトリに定義する決まりになっており、 `components/` 配下のコンポーネントは `pages/` のvueファイルから自動でimportして利用することができます。

- [Components Directory | Nuxt](https://nuxt.com/docs/guide/directory-structure/components)


アラート表示を行う `front/components/Alert.vue` を実装してみましょう

呼び出し元からコンポーネント内のプロパティにアクセスする場合は `defineExpose()` を利用します。 `defineExpose()` は指定されたプロパティを外部に公開できます。

- [defineExpose() | Vue.js](https://vuejs.org/api/sfc-script-setup.html#defineexpose) 

```vue
<!-- *** front/components/Alert.vue *** -->
<template>
  <div style="position: relative">
    <div class="hp_alert_wrapper px-3">
      <!-- itemsの中でshow = trueのアラートを表示する -->
      <div v-for="item in items">
        <v-alert
          class="mb-3"
          v-model="item.show"
          :type="item.type"
          closable
          dismissible >{{ item.body }}</v-alert>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
type AlertType = "error" | "success" | "info" | "warning"

interface AlertItem {
  show: boolean
  type: AlertType
  body: any
}

// アラートを管理する配列
const items = ref<AlertItem[]>([])

// アラートを追加する関数
function alert( alertType: AlertType, message: any) {
  items.value.push({
    show: true,
    type: alertType,
    body: message,
  })
}

// 外部に公開する関数を定義
// defineExpose: https://vuejs.org/api/sfc-script-setup.html#defineexpose
defineExpose({
  error: (message: any) => alert("error", message),
  success: (message: any) => alert("success", message),
  info: (message: any) => alert("info", message),
  warning: (message: any) => alert("warning", message),
 })
</script>

<style>
.hp_alert_wrapper {
  z-index: 100;
  left: 0px;
  top: 0px;
  width: 100%;
  position: absolute;
}
</style>
```

`front/pages/login.vue` から `front/components/Alert.vue` を利用してみましょう。  

```vue
<!-- *** front/pages/login.vue *** -->

<template>
<div>
  <!-- 追加: Alertコンポーネントを配置。 scriptで参照できるようにref属性を指定 -->
  <Alert ref="alert" />
  <!-- ... 略 ... -->
</div>
</template>

<script setup lang="ts">

const username = ref<string>("")
const password = ref<string>("")
const alert = ref<any>(null)  // 追加:  Alert要素のref属性の値を変数名として初期化


interface LoginResponse {
  access_token: string
  token_type: string
}

async function submit() {
  const { data, pending, error, refresh } = await useAsyncData<LoginResponse>(
    // ... 略 ...
  )
  if (!data.value || error.value) {
    alert.value.error(error.value)  // 追加: ログイン失敗時にアラートを表示
    console.error(error.value)
    return
  }
  useAuth().login(data.value.access_token)
  useRouter().push({ path: "/"})
}
</script>
```

# ■ フォームにバリデーションを追加

フォームのバリデーションにはいくつか方法がありますが、今回はVuetifyにデフォルトで用意されている方法を使います。

- [Form - Rules | Vuetify](https://vuetifyjs.com/en/components/forms/#rules)


まずは `utils/rules.ts` にフォーム共通で利用できるバリデーション関数を実装します。
バリデーション関数は、 `(v: string) => boolean | string` と定義します。
引数にバリデーション対象の文字列、戻り値に `boolean | string` を取り、バリデーションの結果がOKであれば `true` 、 NGであれば `string` (エラーメッセージ)を返します。


```ts
// --- front/utils/rules.ts ---

export const useRules = () => {
  return ValidationRules
}

class ValidationRules {
  // 必須入力のバリデーション
  public static required(v: string) {
    return !!v || "Required."
  }

  // 文字列長の最大値のバリデーション
  public static maxLength(n: number) {
    return (v: string) => {
      return (v && v.length <= n) || `Must be less than ${n} characters.`
    }
  }

  // 文字列長の最小値のバリデーション
  public static minLength(n: number) {
    return (v: string) => {
      return (v && v.length >= n) || `Must be more than ${n} characters.`
    }
  }

  // 数値の最大値のバリデーション
  public static max(n: number) {
    return (v: string | number) => {
      const num = typeof v === "string" ? parseInt(v) : v
      return (!isNaN(num) && num <= n) || `Must be less than ${n}.`
    }
  }

  // 数値の最小値のバリデーション
  public static min(n: number) {
    return (v: string | number) => {
      const num = typeof v === "string" ? parseInt(v) : v
      return (!isNaN(num) && num >= n) || `Must be more than ${n}.`
    }
  }
}
```

`front/utils/rules.ts` を使って、ログインフォームにバリデーションを設定しましょう。

1. `v-text-field` の `rule` 属性に先ほど定義したバリデーション関数を配列で渡します。  
2. `v-form` の `ref` 属性と同じ変数名で `ref<any>()` を初期化し、 `v-form` の参照オブジェクトを作成します。  
  テンプレートのref属性に指定した値を変数名としてrefオブジェクトを作成すると、テンプレートへの参照が作成されます。  
  この参照を利用できるのは、テンプレートの描画が完了した後になります。(onMountedないしはonUpdatedで利用できます)  
  [Template Refs](https://vuejs.org/guide/essentials/template-refs.html#accessing-the-refs)
3. `v-form` の参照から `validate()` を呼び出すとバリデーションを実行できます。  


```vue
<!-- *** front/pages/login.vue *** -->

<template>
  <!-- ... 略 ... -->
        <v-form ref="loginForm" lazy-validation>
          <!-- rules属性にバリデーション関数の配列を指定 -->
          <v-text-field
            v-model="username"
            label="Username"
            :rules="[rules.required]"
          ></v-text-field>
          <v-text-field
            v-model="password"
            label="Password"
            type="password"
            :rules="[rules.required]"
          ></v-text-field>
  <!-- ... 略 ... -->
</template>

<script setup lang="ts">
// ... 略 ...


const username = ref<string>("")
const password = ref<string>("")
const alert = ref<any>(null)
const loginForm = ref<any>(null)  // 追加: v-form要素のref属性の値を変数名として初期化 (v-formの参照)
const rules = useRules()  // 追加: バリデーション関数

// ... 略 ...

async function submit() {
  // loginForm.value.validate()  バリデーション実行
  // loginForm.value.resetValidation()  バリデーションの表示のリセット
  // loginForm.value.reset()  入力値とバリデーション表示両方のリセット
  const {valid, errors} = await loginForm.value.validate()  // 追加: バリデーション実行
  if (!valid) {
    return
  }
  // ... 略 ...
}
</script>
```

# ■ APIアクセスの共通化

ユニバーサルレンダリングを採用する場合、APIへのアクセスはサーバーサイドとクライアントサイドどちらからも行われますが、どちらから行うかで送信先のホスト指定が変わってきます。  
※ サーバーサイドなら `localhost` 、クライアントサイドなら外部に公開されているホスト名となります。

また、認証トークンの付与やパラメータのシリアライズなど、リクエスト時に必ず行う処理は以外と多く、それらをリクエスト毎に実装するのは冗長ですしメンテナンス性も低下します。

ここでは、APIアクセスをより簡単に利用できるように `utils/` 配下にapiにアクセス用の共通ユーティリティを実装していきましょう。

## # Runtime Config

- [Exposing Runtime Config | Nuxt](https://nuxt.com/docs/guide/going-further/runtime-config)

Nuxtアプリ内でグローバルに参照可能な変数を定義するにはRuntime Configを利用します。  
Runtime Config はNuxtアプリ内で参照できる変数を定義しておける仕組みで、 `runtimeConfig` は `nuxt.config.ts` に下記のように記述します。  

※ 基本的にはサーバーサイドでのみ参照可能ですが、 `public` 配下に定義した変数のみ、サーバーサイドとクライアントサイド両方で参照可能になります。

```ts
export default defineNuxtConfig({
  runtimeConfig: {
    // サーバーサイドでのみ参照可能
    apiSecret: '123',
    // public配下はサーバーサイド、クライアントサイド両方で参照可能
    public: {
      apiBase: '/api'
    }
  }
})

```

`runtimeConfig` の利用には `useRuntimeConfig()` を利用します。

- [useRuntimeConfig | Nuxt](https://nuxt.com/docs/api/composables/use-runtime-config)

```vue
<script setup lang="ts">
const config = useRuntimeConfig()
console.log(runtimeConfig.apiSecret)
console.log(runtimeConfig.public.apiBase)
</script>
```

## # Runtime Configにサーバーサイド・クライアントサイドそれぞれのベースURLを設定

Runtime ConfigにサーバーサイドでのAPIリクエストで利用されるベースURLと、クライアントサイドで利用されるベースURLを設定しましょう。

```ts
// --- front/nuxt.config.ts ---

// ... 略 ...

export default defineNuxtConfig({
  // ... 略 ...
  // 実行時参照したいグローバルな変数を定義
  runtimeConfig: {
    public: {
      clientBaseUrl: '//localhost:8018/api/v1',
      serverBaseUrl: 'http://localhost:8018/api/v1',
    }
  },
})
```

## # APIアクセスユーティリティを作成

`process.client` は現在の実行環境がクライアントサイドかサーバーサイドかを判断できます。  

```ts
// --- front/utils/api.ts ---

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE"
type QueryString = { [key: string]: string | number | boolean | string[] | number[] | boolean[] | null }
type Headers = { [key: string]: string }
type RequestBody = { [key: string]: any } | FormData

// ユーティリティを外部から利用できるように useApi() を公開
export const useApi = () => {
  return Api
}

class Api {
  // GETリクエストを送信するメソッド
  public static async get<T>( key: string, path: string, params: QueryString = {}, headers: Headers = {}) {
    // paramsをクエリパラメータの形式に変換する (例: {a: 1, b: 2} => "a=1&b=2")
    let query = Object.entries(params)
      .map(([k, v]) => {
        if (v instanceof Array) {
            return v.map((e) => `${k}=${encodeURIComponent(e)}`)
        } else {
            return `${k}=${encodeURIComponent(v ?? "")}`
        }
      })
      .flat()
      .join("&")
    let pathWithQuery = query.length > 0 ? `${path}?${query}` : path
    return Api.fetch<T>(key, "GET", pathWithQuery, null, headers)
  }

  // POSTリクエストを送信するメソッド
  public static async post<T>(key: string, path: string, params: RequestBody = {}, headers: Headers = {}) {
    let body = (params instanceof FormData) ? params : JSON.stringify(params)
    return Api.fetch<T>(key, "POST", path, body, headers)
  }

  // PUTリクエストを送信するメソッド
  public static async put<T>(key: string, path: string, params: RequestBody = {}, headers: Headers = {}) {
    let body = (params instanceof FormData) ? params : JSON.stringify(params)
    return Api.fetch<T>(key, "PUT", path, body, headers)
  }

  // DELETEリクエストを送信するメソッド
  public static async delete<T>(key: string, path: string, params: RequestBody = {}, headers: Headers = {}) {
    let body = (params instanceof FormData) ? params : JSON.stringify(params)
    return Api.fetch<T>(key, "DELETE", path, body, headers)
  }

  // APIリクエストを送信するメソッド
  private static async fetch<T>( key: string, method: HttpMethod, path: string, body: any, headers: Headers = {}) {
    const {clientBaseUrl, serverBaseUrl} = useRuntimeConfig().public;
    // RuntimeConfigに設定したベースURLを利用してクライアントサイドとサーバーサイドで宛先ホストを変更する
    // process.client で現在の実行環境がクライアントサイドかサーバーサイドかを判定できる
    const url = process.client ? `${clientBaseUrl}${path}` : `${serverBaseUrl}${path}`

    // 認証トークンを付与
    if (useAuth().authenticated()) {
      headers.Authorization = `Bearer ${useAuth().getToken()}`
    }

    // リクエスト送信
    return await useAsyncData<T>(
      key,
      () => {
        return $fetch(url, {
          method: method,
          headers: headers,
          body: body,
        })
      },
    )

  }
}
```
## # ユーティリティを利用してログインを行う

APIアクセスユーティリティを利用してトークン取得を行うよう、 `login.vue` を修正しましょう。

```vue
<!-- *** front/pages/login.vue *** -->

<!-- ... 略 ... -->

<script setup lang="ts">

// ... 略 ...

async function submit() {
  const {valid, errors} = await loginForm.value.validate()
  if (!valid) {
    return
  }

  // 変更: useApiを利用してトークン取得APIにアクセスするように変更
  let form = new FormData()
  form.append("username", username.value)
  form.append("password", password.value)
  const { data, pending, error, refresh } = await useApi().post<LoginResponse>("login", "/token", form)
  // 変更: ここまで

  if (!data.value || error.value) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  useAuth().login(data.value.access_token)
  useRouter().push({ path: "/"})
}
</script>
```
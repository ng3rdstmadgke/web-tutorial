[Chapter11] アイテム・ユーザー管理ページ(CRUD)の実装
--
[top](../../README.md)

# Note

このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter11/src` をルートディレクトリとして解説します。

chapter10では、アイテム・ユーザー管理ページを実装します。

# ■ アプリの起動

Nuxtサーバーは run.sh からも起動可能なので、APIサーバーと合わせて起動してみましょう

```bash
# ※ 起動していない場合のみ
./bin/mysql.sh

# 開発用shellを起動
./bin/run.sh chapter11 --mode shell

# データベースの初期化
./bin/init-database.sh

exit

# APIサーバーとNuxtサーバーを起動
./bin/run.sh chapter11 --mode app
```

ブラウザから NuxtサーバーとAPIサーバーにアクセスしてみましょう。

- Nuxtサーバー: http://localhost:3000/
- APIサーバー: http://localhost:8018/docs

```bash
# 開発用shellを起動
./bin/run.sh chapter11 --mode shell

# ディレクトリ作成
cd front
mkdir -p assets components composables layouts middleware modules pages plugins utils
```

# ■ アイテムページで利用するAPIをまとめたコンポーザブル

## コンポーザブル

- [Composables Directory](https://nuxt.com/docs/guide/directory-structure/composables#composables-directory)

コンポーザブル(composables) とはVueコンポーネントに合成(compose) 可能な汎用化された関数のことを指します。  
コンポーザブルはVueコンポーネントで扱うデータや手続きを関数として提供し、処理の詳細をコンポーネントから隠ぺいする責務を負います。

コンポーザブルは `components/` 配下に実装し、 `utils/` 配下のリソースと同様に自動インポートの対象となります。

## アイテムAPIにアクセスするコンポーザブルの実装

itemページのvueコンポーネントから利用される、アイテムAPIにアクセスするコンポーザブルを実装しましょう。

```ts
// --- front/composables/itemApi.ts ---

// リアイテム作成時のリクエストボディの型定義
interface ItemPost {
  title: string
  content: string
}

// アイテム更新時のリクエストボディの型定義
interface ItemPut {
  id: number
  title: string
  content: string
}

// アイテム取得時のレスポンスボディの型定義
interface ItemResponse {
  id: number
  title: string
  content: string
}

// useItemApiの名前で関数をエクスポート
export const useItemApi = () => {
  return {
    // アイテム一覧取得
    async getAll() {
      return useApi().get<ItemResponse[]>("getItems", "/items/")
    },
    // 指定したIDのアイテム取得
    async get(id: number) {
      return useApi().get<ItemResponse>("getItem", `/items/${id}`)
    },
    // アイテム作成
    async create(item: ItemPost) {
      return useApi().post<ItemResponse>("createItem", "/items/", item)
    },
    // アイテム更新
    async update(item: ItemPut) {
      return useApi().put<ItemResponse>("updateItem", `/items/${item.id}`, item)
    },
    // アイテム削除
    async delete(id: number) {
      return useApi().delete<any>("deleteItem", `/items/${id}`)
    }
  }
}
```

# ■ アイテム一覧画面の実装

アイテム一覧画面を実装します。


- 利用するVuetifyのコンポーネント
  - [Flex (要素を横並びにする機能) | Vuetify](https://vuetifyjs.com/en/styles/flex/)
  - [v-table - Tables (テーブル) | Vuetify](https://vuetifyjs.com/en/components/tables/)
  - [v-btn - Buttons (ボタン) | Vuetify](https://vuetifyjs.com/en/components/buttons/)
  - [v-icon - Icons (アイコン) | Vuetify](https://vuetifyjs.com/en/components/icons/)

```vue
<!-- *** front/pages/items/index.vue *** -->

<template>
  <div>
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">Items</div>
    </div>
    <div class="d-flex justify-end">
      <div class="mr-3">
        <v-btn :icon="mdiRefresh" @click="refreshItems"></v-btn>
      </div>
      <div>
        <v-btn color="primary" :icon="mdiPlusBoxMultipleOutline" link to="/items/create"></v-btn>
      </div>
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
          <td><NuxtLink :to="`/items/${item.id}`">{{ item.id }}</NuxtLink></td>
          <td>{{ item.title }}</td>
          <td>
            <div class="d-flex">
              <div>
                <v-btn icon flat link :to="`/items/${item.id}/edit`">
                  <v-icon color="warning" :icon="mdiNoteEditOutline"></v-icon>
                </v-btn>
              </div>
              <div>
                <v-btn icon flat>
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
// 明示的なインポートは不要だが、説明のために説明
import {useItemApi} from '@/composables/itemApi'
import { mdiPlusBoxMultipleOutline, mdiNoteEditOutline, mdiDeleteForeverOutline, mdiRefresh } from '@mdi/js'

// ミドルウェアによる認証チェック
definePageMeta({
  middleware: ["auth"]
})

const alert = ref<any>(null)  // Alertコンポーネントのref

// アイテム一覧取得
const { data: items, pending, error: getItemsError, refresh: refreshItems } = await useItemApi().getAll()

onMounted(() => {
  // アイテム一覧の取得に失敗した場合のエラー処理
  if (getItemsError.value instanceof Error) {
    alert.value.error(getItemsError.value)
    console.error(getItemsError.value)
    return
  }
})
</script>
```

Topページにアクセスしたときに、アイテム一覧ページにリダイレクトするように修正しましょう。

```vue
<!-- *** front/pages/index.vue *** -->

<template>
</template>

<script setup lang="ts">
// アイテム一覧にリダイレクト
useRouter().push({path: "/items/"})
</script>
```

# ■ アイテム作成画面の実装

アイテム作成画面を実装します。

- 利用するVuetifyのコンポーネント
  - [v-form - Form (フォーム) | Vuetify](https://vuetifyjs.com/en/components/forms/)
  - [v-text-field - Text fields (テキスト入力フォーム) | Vuetify](https://vuetifyjs.com/en/components/text-fields/)
  - [v-textarea - Textareas](https://vuetifyjs.com/en/components/textareas/)
  - [v-btn - Buttons (ボタン) | Vuetify](https://vuetifyjs.com/en/components/buttons/)
  - [v-sheet - Sheets (枠) | Vuetify](https://vuetifyjs.com/en/components/sheets/)

```vue
<!-- *** front/pages/items/create.vue *** -->
<template>
  <div>
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">Create item</div>
    </div>
    <v-sheet class="mx-auto">
      <v-form ref="form" @submit.prevent="submit">
        <v-text-field
          v-model="title"
          variant="outlined"
          label="title"
          :rules="[rules.required, rules.maxLength(100)]"
          clearable
          dense
          ></v-text-field>
        <v-textarea
          v-model="content"
          variant="outlined"
          :rules="[rules.required, rules.maxLength(200)]"
          label="content"
          clearable
          dense
        ></v-textarea>
        <v-btn
          color="primary"
          type="submit"
        >作成</v-btn>
      </v-form>

    </v-sheet>
  </div>
</template>

<script setup lang="ts">
// ミドルウェアによる認証チェック
definePageMeta({
  middleware: ["auth"]
})

const title = ref<string>("")
const content = ref<string>("")
const alert = ref<any>(null)  // Alertコンポーネントのref
const form = ref<any>(null)   // v-formのref
const rules = useRules()  // フォームのバリデーション関数を管理するクラス

// アイテム作成
async function submit(event: Event) {
  // フォームのバリデーション
  const {valid, errors} = await form.value.validate()
  if (!valid) {
    return
  }

  // アイテム作成APIの呼び出し
  const { data, pending, error, refresh } = await useItemApi().create({
    title: title.value,
    content: content.value,
  })
  // エラーならアラート表示
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // 成功ならアイテム一覧にリダイレクト
  useRouter().push("/items/")
}
</script>
```


# ■ アイテム詳細画面の実装


アイテム詳細画面を実装します。

- 利用するVuetifyのコンポーネント
  - [Flex (要素を横並びにする機能) | Vuetify](https://vuetifyjs.com/en/styles/flex/)
  - [v-card - Cards (カード) | Vuetify](https://vuetifyjs.com/en/components/cards/)
  - [v-btn - Buttons (ボタン) | Vuetify](https://vuetifyjs.com/en/components/buttons/)
  - [v-icon - Icons (アイコン) | Vuetify](https://vuetifyjs.com/en/components/icons/)

```vue
<!-- *** front/pages/items/[itemId]/index.vue *** -->

<template>
  <div >
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">Item (id={{ item?.id }})</div>
    </div>
    <div class="d-flex justify-end mb-3">
      <div class="mr-3">
        <v-btn :icon="mdiNoteEditOutline" color="warning" link :to="`/items/${item?.id}/edit`"></v-btn>
      </div>
      <div>
        <v-btn :icon="mdiDeleteForeverOutline" color="error"></v-btn>
      </div>
    </div>
    <v-card >
      <v-card-title>
        {{ item?.title }}
      </v-card-title>
      <v-card-text>
        {{ item?.content }}
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { mdiNoteEditOutline, mdiDeleteForeverOutline } from '@mdi/js'

// ミドルウェアによる認証チェック
definePageMeta({
  middleware: ["auth"]
})

// パスパラメータ(itemId)を取得
const {itemId} = useRoute().params

const alert = ref<any>(null)  // Alertコンポーネントのref

// アイテム取得
const { data: item, pending, error: getItemError, refresh } = await useItemApi().get(itemId)

// アイテムの取得に失敗した場合のエラー処理
onMounted(() => {
  if (getItemError.value instanceof Error) {
    alert.value.error(getItemError.value)
    console.error(getItemError.value)
    return
  }
})
</script>
```


# ■ アイテム編集画面の実装

アイテム編集画面を実装します。

- 利用するVuetifyのコンポーネント
  - [v-sheet - Sheets (枠) | Vuetify](https://vuetifyjs.com/en/components/sheets/)
  - [v-text-field - Text fields | Vuetify](https://vuetifyjs.com/en/components/text-fields/)
  - [v-textarea - Textareas](https://vuetifyjs.com/en/components/textareas/)
  - [v-btn - Buttons (ボタン) | Vuetify](https://vuetifyjs.com/en/components/buttons/)

```vue
<!-- *** front/pages/items/[itemId]/edit.vue *** -->

<template>
  <div>
    <Alert ref="alert"></Alert>
    <div class="mb-3">
      <div class="text-h4">Edit item (id={{ item!.id }})</div>
    </div>
    <v-sheet class="mx-auto">
      <v-form ref="form" @submit.prevent="submit(item!.id)">
        <v-text-field
          v-model="item!.title"
          variant="outlined"
          label="title"
          :rules="[rules.required, rules.maxLength(100)]"
          clearable
          dense
          ></v-text-field>
        <v-textarea
          v-model="item!.content"
          variant="outlined"
          label="content"
          :rules="[rules.required, rules.maxLength(200)]"
          clearable
          dense
        ></v-textarea>
        <v-btn
          color="primary"
          type="submit"
        >更新</v-btn>
      </v-form>

    </v-sheet>
  </div>
</template>

<script setup lang="ts">
// ミドルウェアによる認証チェック
definePageMeta({
  middleware: ["auth"]
})

// パスパラメータを取得
const {itemId} = useRoute().params

const alert = ref<any>(null)  // Alertコンポーネントのref
const form = ref<any>(null)   // v-formのref
const rules = useRules()  // フォームのバリデーション関数を管理するクラス

// アイテム取得
const { data: item, pending, error: getItemError, refresh } = await useItemApi().get(itemId)

onMounted(() => {
  // アイテムの取得に失敗した場合のエラー処理
  if (getItemError.value instanceof Error) {
    alert.value.error(getItemError.value)
    console.error(getItemError.value)
    return
  }
})

// アイテム更新
async function submit(id: number) {
  // フォームのバリデーション
  const {valid, errors} = await form.value.validate()
  if (!valid) {
    return
  }

  // アイテム更新APIの呼び出し
  const { data, pending, error, refresh } = await useItemApi().update(item.value)
  // エラーならアラート表示
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // 成功ならアイテム一覧ページに遷移
  useRouter().push("/items/")
}
</script>
```


# ■ アイテム削除機能の実装

削除機能は削除画面を作るわけではなく、ゴミ箱アイコンをクリックしたときに確認ダイアログが表示されて、確認したら削除APIを送信するという方式で実装していきます。


まずは、共通コンポーネントとして `components/ConfirmDialog.vue` に確認ダイアログを実装してみましょう。


- [defineExpose() | Vue.js](https://vuejs.org/api/sfc-script-setup.html#defineexpose)  
コンポーネント内のプロパティに外部からアクセスしたい場合は `defineExpose` でプロパティを公開します。
- [defineProps() | Vue.js](https://ja.vuejs.org/api/sfc-script-setup.html#defineprops-defineemits)  
コンポーネントの呼び出し時に属性としてしていするプロパティを定義します。  
`withDefaults(defineProps(), {...})` とすることでデフォルト値を定義できます。
- [defineEmits() | Vue.js](https://ja.vuejs.org/api/sfc-script-setup.html#defineprops-defineemits)  
このコンポーネントが発するイベントを定義します。  
イベントは `emit("イベント名", 引数1, ...)` のように発生させます。


- 利用するVuetifyのコンポーネント
  - [v-dialog - Dialogs (ダイアログ)](https://vuetifyjs.com/en/components/dialogs/)
  - [v-card - Cards (カード) | Vuetify](https://vuetifyjs.com/en/components/cards/)
  - [v-btn - Buttons (ボタン) | Vuetify](https://vuetifyjs.com/en/components/buttons/)

```vue
<!-- *** front/components/ConfirmDialog.vue *** -->

<template>
  <!--
    v-modelのdialogがtrueなら表示、falseなら非表示
    https://vuetifyjs.com/ja/components/dialogs/
  -->
  <v-dialog v-model="dialog" persistent max-width="400px">
    <v-card>
      <v-card-title>
        <span class="headline">{{props.title}}</span>
      </v-card-title>
      <v-card-text>
        {{props.message}}
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn :color="props.colorCancel"  @click="confirm(false)">{{cancelBtn}}</v-btn>
        <v-btn :color="props.colorConfirm" @click="confirm(true)">{{confirmBtn}}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
interface Props {
  title: string
  message: string
  cancelBtn: string
  confirmBtn: string
  colorCancel: "primary" | "secondary" | "error" | "warning" | "info" | "success"
  colorConfirm: "primary" | "secondary" | "error" | "warning" | "info" | "success"
}


// ダイアログの表示・非表示のコントロール
const dialog = ref<boolean>(false)
// コンポーネントの呼び出し元から受け取るパラメータ
let parameters: any = {}

// 親コンポーネントがダイアログを開くときに呼び出す関数
function open(v: any = {}) {
  dialog.value = true // ダイアログを表示
  parameters = v
}

// ダイアログのボタンがクリックされたときに呼び出す関数
function confirm(confirm: boolean) {
  dialog.value = false // ダイアログを非表示
  // confirmイベントを発生させる
  emit("confirm", confirm, parameters)
}

// propsはdefinePropsで定義する。デフォルト値はwithDefaultsで定義する。
// defineProps: https://vuejs.org/api/sfc-script-setup.html#defineprops-defineemits
const props = withDefaults(defineProps<Props>(), {
  title: "",
  message: "",
  cancelBtn: "Cancel",
  confirmBtn: "OK",
  colorCancel: "primary",
  colorConfirm: "error",
})

// イベントを発生させたいときは defineEmits を使う。
// defineEmits: https://vuejs.org/api/sfc-script-setup.html#defineprops-defineemits
const emit = defineEmits<{
  // confirmイベントを定義
  confirm: [ok: boolean, parameters: any], // イベントの引数を名前付きタプルで定義
}>()

// カスタムコンポーネント内の関数などを呼びたいときは defineExpose を使って、明示的に公開する必要がある。
// defineExpose: https://vuejs.org/api/sfc-script-setup.html#defineexpose
defineExpose({
  open: open,
})
</script>
```

アイテム一覧の削除ボタンに削除機能を実装してみましょう。

処理の流れとしては下記のようになります。

1. 削除ボタンをクリックしたら確認ダイアログを表示
1. 「削除」がクリックされたら削除APIを送信。「キャンセル」がクリックされたら何もしない。


```vue
<!-- *** front/pages/items/index.vue *** -->
<template>
  <div>
    <!-- ... 略 ... -->

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
          <td><NuxtLink :to="`/items/${item.id}`">{{ item.id }}</NuxtLink></td>
          <td>{{ item.title }}</td>
          <td>
            <div class="d-flex">
              <div>
                <v-btn icon flat link :to="`/items/${item.id}/edit`">
                  <v-icon color="warning" :icon="mdiNoteEditOutline"></v-icon>
                </v-btn>
              </div>
              <div>
                <!-- 追加: @click="confirmDeletion.open({id: item.id})"
                  クリックイベントで、confirmDeletion.open() を実行。 引数にアイテムIDを指定。
                  open() は defineExposeで外部公開している関数。
                -->
                <v-btn icon flat @click="confirmDeletion.open({id: item.id})">
                  <v-icon color="error" :icon="mdiDeleteForeverOutline"></v-icon>
                </v-btn>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </v-table>

    <!-- 追加:
      ConfirmDialogコンポーネント。 definePropsに定義したプロパティを属性として指定。
      defineEmits() でconfirmイベントを定義しているので、 @confirm="deleteItem" と設定し、
      confirmイベント発生時にdeleteItem関数が実行されるようにする。
      -->
    <ConfirmDialog
      title="アイテムの削除"
      message="本当に削除しますか"
      confirmBtn="削除"
      cancelBtn="キャンセル"
      colorCancel="primary"
      colorConfirm="error"
      ref="confirmDeletion"
      @confirm="deleteItem">
    </ConfirmDialog>
  </div>
</template>

<script setup lang="ts">
// ... 略 ...

// 以下追加

const confirmDeletion = ref<any>(null)  // ConfirmDialogコンポーネントの参照

// アイテム削除関数
async function deleteItem(confirm: boolean, params: {id: number}) {
  // 確認ダイアログで承認されたかをチェック
  if (!confirm) {
    return
  }
  // アイテム削除APIを呼び出し
  const { error } = await useItemApi().delete(params.id)
  // エラーの場合はアラート表示
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // 削除に成功したらアイテム一覧を再取得
  refreshItems()
}
</script>
```

アイテム詳細の削除ボタンに削除機能を実装しましょう。

```vue
<!-- *** front/pages/items/[itemId]/index.vue *** -->

<template>
  <div >
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">Item (id={{ item?.id }})</div>
    </div>
    <div class="d-flex justify-end mb-3">
      <div class="mr-3">
        <v-btn :icon="mdiNoteEditOutline" color="warning" link :to="`/items/${item?.id}/edit`"></v-btn>
      </div>
      <div>
        <!-- 追加: @click="confirmDeletion.open({id: item?.id})" -->
        <v-btn :icon="mdiDeleteForeverOutline" color="error" @click="confirmDeletion.open({id: item?.id})"></v-btn>
      </div>
    </div>

    <!-- ... 略 ... -->

    <!-- 追加 -->
    <ConfirmDialog
      title="アイテムの削除"
      message="本当に削除しますか"
      confirmBtn="削除"
      cancelBtn="キャンセル"
      colorCancel="primary"
      colorConfirm="error"
      ref="confirmDeletion"
      @confirm="deleteItem">
    </ConfirmDialog>
  </div>
</template>

<script setup lang="ts">
// ... 略 ...
const confirmDeletion = ref<any>(null)  // ConfirmDialogコンポーネントの参照

// アイテム削除
async function deleteItem(confirm: boolean, params: {id: number}) {
  // 確認ダイアログで承認されたかをチェック
  if (!confirm) {
    return
  }
  // アイテム削除APIを呼び出し
  const { error } = await useItemApi().delete(params.id)
  // エラーの場合はアラートを表示
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // 削除後はアイテム一覧画面に遷移
  useRouter().push({path: "/items/"})
}
</script>
```


# ■ ユーザー管理ページの実装

ユーザー管理ページはアイテム管理ページと同じ要領で実装すればいいので詳細な解説は省き、コード飲みを記載します。

ユーザー管理APIにアクセスするためのコンポーザブル

```ts
// --- front/composables/userApi.ts ---
// ユーザー作成時のリクエストボディの型定義
interface UserPost {
  username: string
  password: string
  age: number
  role_ids: number[]
}

// ユーザー更新時のリクエストボディの型定義
interface UserPut {
  id: number
  password: string
  age: number
  role_ids: number[]
}

// ユーザー取得時のレスポンスボディの型定義
interface UserResponse {
  id: number
  username: string
  age: number
  roles: {
    id: number,
    name: string
  }[]
}

// useUserApiの名前で関数をエクスポート
export const useUserApi = () => {
  return {
    // ユーザー一覧取得
    async getAll() {
      return useApi().get<UserResponse[]>("getUsers", "/users/")
    },
    // 指定したIDのユーザー取得
    async get(id: number) {
      return useApi().get<UserResponse>("getUser", `/users/${id}`)
    },
    // ユーザー作成
    async create(user: UserPost) {
      return useApi().post<UserResponse>("createUser", "/users/", user)
    },
    // ユーザー更新
    async update(user: UserPut) {
      return useApi().put<UserResponse>("updateUser", `/users/${user.id}`, user)
    },
    // ユーザー削除
    async delete(id: number) {
      return useApi().delete<any>("deleteUser", `/users/${id}`)
    }
  }
}
```

ユーザー一覧ページ

```vue
<!-- *** front/pages/users/index.vue *** -->
<template>
  <div>
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">Users</div>
    </div>
    <div class="d-flex justify-end">
      <div class="mr-3">
        <v-btn :icon="mdiRefresh" @click="refreshUsers"></v-btn>
      </div>
      <div>
        <v-btn color="primary" :icon="mdiPlusBoxMultipleOutline" link to="/users/create"></v-btn>
      </div>
    </div>
    <v-table>
      <thead>
        <tr>
          <th>id</th>
          <th>username</th>
          <th>age</th>
          <th>roles</th>
          <th>actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td><NuxtLink :to="`/users/${user.id}`">{{ user.id }}</NuxtLink></td>
          <td>{{ user.username }}</td>
          <td>{{ user.age }}</td>
          <td>{{ user.roles.map((e) => e.name).join(", ") }}</td>
          <td>
            <div class="d-flex">
              <div>
                <v-btn icon flat link :to="`/users/${user.id}/edit`">
                  <v-icon color="warning" :icon="mdiNoteEditOutline"></v-icon>
                </v-btn>
              </div>
              <div>
                <v-btn icon flat @click="confirmDeletion.open({id: user.id})">
                  <v-icon color="error" :icon="mdiDeleteForeverOutline"></v-icon>
                </v-btn>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </v-table>
    <!-- 削除確認ダイアログ -->
    <ConfirmDialog
      title="ユーザーの削除"
      message="本当に削除しますか"
      confirmBtn="削除"
      cancelBtn="キャンセル"
      colorCancel="primary"
      colorConfirm="error"
      ref="confirmDeletion"
      @confirm="deleteUser">
    </ConfirmDialog>
  </div>
</template>

<script setup lang="ts">
import { mdiPlusBoxMultipleOutline, mdiNoteEditOutline, mdiDeleteForeverOutline, mdiRefresh } from '@mdi/js'

// ミドルウェアによるログインチェック
definePageMeta({ middleware: ["auth"] })

const confirmDeletion = ref<any>(null)  // ConfirmDialogコンポーネントのref
const alert = ref<any>(null)  // Alertコンポーネントのref

// ユーザー一覧取得
const { data: users, pending, error: getUsersError, refresh: refreshUsers } = await useUserApi().getAll()

onMounted(() => {
  // ユーザー一覧の取得に失敗したらアラートを表示
  if (getUsersError.value instanceof Error) {
    alert.value.error(getUsersError.value)
    console.error(getUsersError.value)
    return
  }
})

// ユーザー削除関数
async function deleteUser(confirm: boolean, params: {id: number}) {
  // キャンセルされた場合は何もしない
  if (!confirm) { return }
  // ユーザー削除APIを呼び出す
  const { error } = await useUserApi().delete(params.id)
  // エラー: アラートを表示
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // 成功: ユーザー一覧を再取得
  refreshUsers()
}
</script>
```

ユーザー作成ページ

```vue
<!-- *** front/pages/users/create.vue *** -->
<template>
  <div>
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">Create user</div>
    </div>
    <v-sheet class="mx-auto">
      <v-form ref="form" @submit.prevent="submit">
        <v-text-field
          v-model="username"
          variant="outlined"
          label="username"
          :rules="[rules.required, rules.maxLength(100)]"
          clearable
          dense
          ></v-text-field>
        <v-text-field
          v-model="password"
          variant="outlined"
          label="password"
          :rules="[rules.required, rules.minLength(8), rules.maxLength(100)]"
          type="password"
          clearable
          dense
        ></v-text-field>
        <v-text-field
          v-model="age"
          variant="outlined"
          label="age"
          :rules="[rules.required, rules.max(150)]"
          type="number"
          clearable
          dense
        ></v-text-field>
        <v-select
          v-model="role_ids"
          variant="outlined"
          label="roles"
          :items="[{id: 1, name: 'SYSTEM_ADMIN'}, {id: 2, name: 'LOCATION_ADMIN'}, {id: 3, name: 'LOCATION_OERATOR'}]"
          item-title="name"
          item-value="id"
          clearable
          multiple
          dense
        ></v-select>
        <v-btn
          color="primary"
          type="submit"
        >作成</v-btn>
      </v-form>
    </v-sheet>
  </div>
</template>

<script setup lang="ts">

// ミドルウェアによるログインチェック
definePageMeta({ middleware: ["auth"] })

const username = ref<string>("")
const password = ref<string>("")
const age = ref<number>(30)
const role_ids = ref<number[]>([])
const alert = ref<any>(null)  // Alertコンポーネントのref
const form = ref<any>(null)   // v-formのref
const rules = useRules()  // バリデーション関数クラス

async function submit() {
  // バリデーション
  const {valid, errors} = await form.value.validate()
  if (!valid) {
    return
  }
  // ユーザー作成APIを呼び出す
  const { data: user, pending, error, refresh } = await useUserApi().create({
    username: username.value,
    password: password.value,
    age: age.value,
    role_ids: role_ids.value,
  })
  // エラー: アラートを表示
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // 成功: ユーザー一覧画面に遷移
  useRouter().push("/users/")
}
</script>

```

ユーザー詳細ページ

```vue
<!-- *** front/pages/users/[userId]/index.vue *** -->
<template>
  <div >
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">User (id={{ user?.id }})</div>
    </div>
    <div class="d-flex justify-end mb-3">
      <div class="mr-3">
        <v-btn :icon="mdiNoteEditOutline" color="warning" link :to="`/users/${user?.id}/edit`"></v-btn>
      </div>
      <div>
        <v-btn :icon="mdiDeleteForeverOutline" color="error" @click="confirmDeletion.open({id: user?.id})"></v-btn>
      </div>
    </div>
    <v-table>
      <thead>
        <tr>
          <th>Parameter</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>id</td>
          <td>{{ user?.id }}</td>
        </tr>
        <tr>
          <td>username</td>
          <td>{{ user?.username }}</td>
        </tr>
        <tr>
          <td>age</td>
          <td>{{ user?.age }}</td>
        </tr>
        <tr>
          <td>roles</td>
          <td>{{ user?.roles.map((r) => r.name).join(", ") }}</td>
        </tr>
      </tbody>
    </v-table>
    <!-- 削除確認ダイアログ -->
    <ConfirmDialog
      title="ユーザーの削除"
      message="本当に削除しますか"
      confirmBtn="削除"
      cancelBtn="キャンセル"
      colorCancel="primary"
      colorConfirm="error"
      ref="confirmDeletion"
      @confirm="deleteUser">
    </ConfirmDialog>
  </div>
</template>

<script setup lang="ts">
import { mdiNoteEditOutline, mdiDeleteForeverOutline } from '@mdi/js'

// ミドルウェアによるログインチェック
definePageMeta({ middleware: ["auth"] })

// パスパラメータを取得
const {userId} = useRoute().params

const confirmDeletion = ref<any>(null)  // ConfirmDialogコンポーネントのref
const alert = ref<any>(null)  // Alertコンポーネントのref

// ユーザー取得
const { data: user, pending, error: getUserError, refresh } = await useUserApi().get(userId)

onMounted(() => {
  // ユーザー取得に失敗したらアラートを表示
  if (getUserError.value instanceof Error) {
    alert.value.error(getUserError.value)
    console.error(getUserError.value)
    return
  }
})

// アイテム削除
async function deleteUser(confirm: boolean, params: {id: number}) {
  // キャンセルされた場合は何もしない
  if (!confirm) { return }
  // 削除APIを呼び出す
  const { error } = await useUserApi().delete(params.id)
  // エラー: アラートを表示
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // 成功: ユーザー一覧ページに遷移
  useRouter().push({path: "/users/"})
}

</script>
```

ユーザー編集ページ

```vue
<!-- *** front/pages/users/[userId]/edit.vue *** -->
<template>
  <div>
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">Create user</div>
    </div>
    <v-sheet class="mx-auto">
      <v-form ref="form" @submit.prevent="submit">
        <v-text-field
          v-model="user!.username"
          variant="outlined"
          label="username"
          :rules="[rules.required, rules.maxLength(100)]"
          dense
          readonly
          ></v-text-field>
        <v-text-field
          v-model="password"
          variant="outlined"
          label="password"
          :rules="[rules.required, rules.minLength(8), rules.maxLength(100)]"
          type="password"
          clearable
          dense
        ></v-text-field>
        <v-text-field
          v-model="user!.age"
          variant="outlined"
          label="age"
          :rules="[rules.required, rules.max(150)]"
          type="number"
          clearable
          dense
        ></v-text-field>
        <v-select
          v-model="role_ids"
          variant="outlined"
          label="roles"
          :items="[{id: 1, name: 'SYSTEM_ADMIN'}, {id: 2, name: 'LOCATION_ADMIN'}, {id: 3, name: 'LOCATION_OERATOR'}]"
          item-title="name"
          item-value="id"
          clearable
          multiple
          dense
        ></v-select>
        <v-btn
          color="primary"
          type="submit"
        >作成</v-btn>
      </v-form>
    </v-sheet>
  </div>
</template>

<script setup lang="ts">
import { useUserApi } from '@/composables/userApi';

// ミドルウェアによるログインチェック
definePageMeta({ middleware: ["auth"] })

// パスパラメータを取得
const {userId} = useRoute().params

const password = ref<string>("")
const age = ref<number>(0)
const role_ids = ref<number[]>([])
const alert = ref<any>(null)  // Alertコンポーネントのref
const form = ref<any>(null)   // v-formのref
const rules = useRules()

// ユーザー取得
const { data: user, pending, error: getUserError, refresh } = await useUserApi().get(userId)
if (user.value) {
  age.value = user.value.age
  role_ids.value = user.value.roles.map((role: any) => role.id)
}

onMounted(() => {
  // ユーザー取得に失敗したらアラートを表示
  if (getUserError.value instanceof Error) {
    alert.value.error(getUserError.value)
    console.error(getUserError.value)
    return
  }
})

// ユーザー更新
async function submit() {
  // バリデーション
  const {valid, errors} = await form.value.validate()
  if (!valid) {
    return
  }
  // ユーザー更新APIを呼び出す
  const { data, pending, error, refresh } = await useUserApi().update({
    id: user.value!.id,
    password: password.value,
    age: user.value!.age,
    role_ids: role_ids.value,
  })
  // エラー: アラートを表示
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // 成功: ユーザー一覧画面に遷移
  useRouter().push("/users/")
}
</script>

```
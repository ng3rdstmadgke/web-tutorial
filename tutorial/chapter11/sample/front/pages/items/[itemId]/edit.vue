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

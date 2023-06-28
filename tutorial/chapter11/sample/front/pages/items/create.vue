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

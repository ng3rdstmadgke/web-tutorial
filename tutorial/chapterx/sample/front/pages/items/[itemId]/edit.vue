<template>
  <div>
    <Alert ref="alert"></Alert>
    <div class="mb-3">
      <div class="text-h4">Edit item (id={{ item.id }})</div>
    </div>
    <v-sheet class="mx-auto">
      <v-form @submit.prevent="submit(item.id)">
        <v-text-field
          v-model="item.title"
          variant="outlined"
          label="title"
          clearable
          dense
          ></v-text-field>
        <v-textarea
          v-model="item.content"
          variant="outlined"
          label="content"
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
import { useItemApi } from '@/composables/itemApi';

definePageMeta({
  middleware: ["auth"]
})

// パスパラメータを取得
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

// アイテム更新
async function submit(id: number) {
  const { data, pending, error, refresh } = await useItemApi().update(item.value)
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  useRouter().push("/items/")
}
</script>

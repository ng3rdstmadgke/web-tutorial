<template>
  <div>
    <Alert ref="updateAlert"></Alert>
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

interface Item {
  id: number
  title: string
  content: string
}

// パスパラメータを取得
const {itemId} = useRoute().params

const updateAlert = ref<any>(null)  // Alertコンポーネントのref


// アイテム取得
const { data: item, pending, error, refresh } = await useItemApi().get(itemId)

// アイテム更新
async function submit(id: number) {
  const { data, pending, error, refresh } = await useItemApi().update(item.value)
  if (error.value instanceof Error) {
    updateAlert.value.alert("error", error.value)
    console.error(error.value)
    return
  }
  useRouter().push("/items/")
}
</script>

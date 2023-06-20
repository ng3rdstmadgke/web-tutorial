<template>
  <div>
    <Alert ref="createAlert" />
    <div class="mb-3">
      <div class="text-h4">Create item</div>
    </div>
    <v-sheet class="mx-auto">
      <v-form @submit.prevent="submit">
        <v-text-field
          v-model="title"
          variant="outlined"
          label="title"
          clearable
          dense
          ></v-text-field>
        <v-textarea
          v-model="content"
          variant="outlined"
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
import { useItemApi } from '@/composables/itemApi';

definePageMeta({
  middleware: ["auth"]
})

const title = ref<string>("")
const content = ref<string>("")
const createAlert = ref<any>(null)  // Alertコンポーネントのref

interface Item {
  id: number
  title: string
  content: string
}

// アイテム作成
async function submit(event: Event) {
  const { data: item, pending, error, refresh } = await useItemApi().create({
    title: title.value,
    content: content.value,
  })
  if (error.value instanceof Error) {
    createAlert.value.alert("error", error.value)
    console.error(error.value)
    return
  }
  useRouter().push("/items/")
}
</script>

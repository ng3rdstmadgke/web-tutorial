<template>
  <div>
    <v-alert v-model="updateError" closable dismissible type="error">{{ updateError }}</v-alert>
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
const updateError = ref<Error | null>(null)


// アイテム取得
const { data: item, pending, error: getError, refresh } = await useAsyncData<Item>(
  "getItem",
  () => {
    // サーバーサイドレンダリング時のURLは "http://" を付けないといけない
    return $fetch(`http://localhost:8018/api/v1/items/${itemId}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${useAuth().getToken()}`,
      },
    })
  },
)

async function submit(id: number) {
  const { data, pending, error, refresh } = await useAsyncData<Item>(
    "updateItem",
    () => {
      return $fetch(`//localhost:8018/api/v1/items/${id}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${useAuth().getToken()}`,
        },
        body: JSON.stringify(item.value)
      })
    }
  )
  if (error.value instanceof Error) {
    updateError.value = error.value
    return
  }
  useRouter().push("/items/")
}
</script>

<template>
  <div>
    <v-alert v-if="createError" dismissible type="error">{{ createError }}</v-alert>
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
definePageMeta({
  middleware: ["auth"]
})

const title = ref<string>("")
const content = ref<string>("")
const createError = ref<Error>()

interface Item {
  id: number
  title: string
  content: string
}

async function submit(event: Event) {
  const { data: item, pending, error: createError, refresh } = await useAsyncData<Item>(
    "createItem",
    () => {
      return $fetch("//localhost:8018/api/v1/items/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${useAuth().getToken()}`,
        },
        body: JSON.stringify({
          title: title.value,
          content: content.value,
        }),
      })
    }
  )
  if (! item.value || createError.value) {
    return
  }
  useRouter().push("/items/")
}
</script>

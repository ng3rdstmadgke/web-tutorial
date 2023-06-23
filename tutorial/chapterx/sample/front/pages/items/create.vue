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
import { useItemApi } from '@/composables/itemApi';

definePageMeta({
  middleware: ["auth"]
})

const title = ref<string>("")
const content = ref<string>("")
const alert = ref<any>(null)  // Alertコンポーネントのref
const form = ref<any>(null)   // v-formのref
const rules = useRules()

interface Item {
  id: number
  title: string
  content: string
}

// アイテム作成
async function submit(event: Event) {
  const {valid, errors} = await form.value.validate()
  if (!valid) {
    return
  }

  const { data: item, pending, error, refresh } = await useItemApi().create({
    title: title.value,
    content: content.value,
  })
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  useRouter().push("/items/")
}
</script>

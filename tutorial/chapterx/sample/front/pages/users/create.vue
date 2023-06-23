<template>
  <div>
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">Create user</div>
    </div>
    <v-sheet class="mx-auto">
      <v-form @submit.prevent="submit">
        <v-text-field
          v-model="username"
          variant="outlined"
          label="username"
          clearable
          dense
          ></v-text-field>
        <v-text-field
          v-model="password"
          variant="outlined"
          label="password"
          type="password"
          clearable
          dense
        ></v-text-field>
        <v-text-field
          v-model="age"
          variant="outlined"
          label="age"
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

definePageMeta({
  middleware: ["auth"]
})

const username = ref<string>("")
const password = ref<string>("")
const age = ref<number>(30)
const role_ids = ref<number[]>([])
const alert = ref<any>(null)  // Alertコンポーネントのref

// アイテム作成
async function submit() {
  const { data: user, pending, error, refresh } = await useUserApi().create({
    username: username.value,
    password: password.value,
    age: age.value,
    role_ids: role_ids.value,
  })
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  useRouter().push("/users/")
}
</script>

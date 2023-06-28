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

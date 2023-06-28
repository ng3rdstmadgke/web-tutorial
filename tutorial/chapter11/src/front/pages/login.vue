<template>
<div>
  <Alert ref="alert" />
  <div class="my-10">
    <v-row justify="center">
      <v-col cols="12" lg="4" sm="6">
      <v-card class="pa-5">
        <v-card-title class="d-flex justify-center mb-3">
          <div>
            <v-img :src="`/logo-no-background.png`" contain height="180"></v-img>
          </div>
        </v-card-title>
        <v-form ref="loginForm" lazy-validation>
          <v-text-field
            v-model="username"
            label="Username"
            :rules="[rules.required]"
          ></v-text-field>
          <v-text-field
            v-model="password"
            label="Password"
            type="password"
            :rules="[rules.required]"
          ></v-text-field>
          <div class="d-flex justify-end">
            <v-btn color="secondary" class="mr-4" type="submit" @click.prevent="submit">login</v-btn>
          </div>
        </v-form>
      </v-card>
      </v-col>
    </v-row>
  </div>
</div>
</template>

<script setup lang="ts">

// テキストフィールドにバインドされるデータ
const username = ref<string>("")
const password = ref<string>("")
const alert = ref<any>(null)  // Alertコンポーネントのref
const loginForm = ref<any>(null)  // v-form要素のref
const rules = useRules()

interface LoginResponse {
  access_token: string
  token_type: string
}

// "LOGIN" ボタンがクリックされたときに呼び出される関数
async function submit() {
  const {valid, errors} = await loginForm.value.validate()
  if (!valid) {
    return
  }

  let form = new FormData()
  form.append("username", username.value)
  form.append("password", password.value)
  const { data, pending, error, refresh } = await useApi().post<LoginResponse>("login", "/token", form)

  // ログイン失敗ならログを出力してreturn
  if (!data.value || error.value) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // ログイン成功ならCookieにトークンをセット
  useAuth().login(data.value.access_token)
  // トップページにリダイレクト
  useRouter().push({ path: "/"})
}
</script>
<template>
<div>
  <v-alert v-if="loginError" dismissible type="error">{{ loginError }}</v-alert>
  <!--
    https://vuetifyjs.com/ja/components/forms/#submit-26-clear3067306e30d030ea30c730fc30b730e730f3

    v-form コンポーネントはref属性を設定することで、3つの関数にアクセスできる
    this.$refs.form.validate(): すべての入力を検証し、すべて有効であるかを確認する
    this.$refs.form.reset(): すべての入力を消去し、バリデーションエラーをリセットする
    this.$refs.form.resetValidation(): 入力バリデーションのみをリセットする
  -->
  <div class="my-10">
    <v-row justify="center">
      <v-col cols="12" lg="4" sm="6">
      <v-card class="pa-5">
        <v-card-title class="d-flex justify-center mb-3">
          <div>
            <v-img :src="`/logo-no-background.png`" contain height="180"></v-img>
          </div>
        </v-card-title>
        <v-form ref="form" lazy-validation>
         <!-- $touch: $dirtyフラグを trueにする -->
          <v-text-field
            v-model="username"
            label="Username"
            required
          ></v-text-field>
          <v-text-field
            v-model="password"
            label="Password"
            required
            type="password"
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
//import { useAuth } from "~/utils/auth"

const username = ref<string>("")
const password = ref<string>("")
const loginError = ref<Error | null>(null)

interface LoginResponse {
  access_token: string
  token_type: string
}

async function submit() {
  const { data, pending, error, refresh } = await useAsyncData<LoginResponse>(
    "getArticles",
    () => {
      let form = new FormData()
      form.append("username", username.value)
      form.append("password", password.value)
      return $fetch("//localhost:8018/api/v1/token", {
        method: "POST",
        headers: {},
        body: form,
      })
    },
    {
      server: false,
    }
  )
  if (! data.value || error.value) {
    loginError.value = error.value
    return
  }
  useAuth().login(data.value.access_token)
  useRouter().push({ path: "/"})
}
</script>
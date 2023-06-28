<template>
  <div>
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">Users</div>
    </div>
    <div class="d-flex justify-end">
      <div class="mr-3">
        <v-btn :icon="mdiRefresh" @click="refreshUsers"></v-btn>
      </div>
      <div>
        <v-btn color="primary" :icon="mdiPlusBoxMultipleOutline" link to="/users/create"></v-btn>
      </div>
    </div>
    <v-table>
      <thead>
        <tr>
          <th>id</th>
          <th>username</th>
          <th>age</th>
          <th>roles</th>
          <th>actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td><NuxtLink :to="`/users/${user.id}`">{{ user.id }}</NuxtLink></td>
          <td>{{ user.username }}</td>
          <td>{{ user.age }}</td>
          <td>{{ user.roles.map((e) => e.name).join(", ") }}</td>
          <td>
            <div class="d-flex">
              <div>
                <v-btn icon flat link :to="`/users/${user.id}/edit`">
                  <v-icon color="warning" :icon="mdiNoteEditOutline"></v-icon>
                </v-btn>
              </div>
              <div>
                <v-btn icon flat @click="confirmDeletion.open({id: user.id})">
                  <v-icon color="error" :icon="mdiDeleteForeverOutline"></v-icon>
                </v-btn>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </v-table>
    <!-- 削除確認ダイアログ -->
    <ConfirmDialog
      title="ユーザーの削除"
      message="本当に削除しますか"
      confirmBtn="削除"
      cancelBtn="キャンセル"
      colorCancel="primary"
      colorConfirm="error"
      ref="confirmDeletion"
      @confirm="deleteUser">
    </ConfirmDialog>
  </div>
</template>

<script setup lang="ts">
import { mdiPlusBoxMultipleOutline, mdiNoteEditOutline, mdiDeleteForeverOutline, mdiRefresh } from '@mdi/js'

// ミドルウェアによるログインチェック
definePageMeta({ middleware: ["auth"] })

const confirmDeletion = ref<any>(null)  // ConfirmDialogコンポーネントのref
const alert = ref<any>(null)  // Alertコンポーネントのref

// ユーザー一覧取得
const { data: users, pending, error: getUsersError, refresh: refreshUsers } = await useUserApi().getAll()

onMounted(() => {
  // ユーザー一覧の取得に失敗したらアラートを表示
  if (getUsersError.value instanceof Error) {
    alert.value.error(getUsersError.value)
    console.error(getUsersError.value)
    return
  }
})

// ユーザー削除関数
async function deleteUser(confirm: boolean, params: {id: number}) {
  // キャンセルされた場合は何もしない
  if (!confirm) { return }
  // ユーザー削除APIを呼び出す
  const { error } = await useUserApi().delete(params.id)
  // エラー: アラートを表示
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // 成功: ユーザー一覧を再取得
  refreshUsers()
}
</script>
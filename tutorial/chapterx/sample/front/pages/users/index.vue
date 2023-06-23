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
// 明示的なインポートは不要だが、IDEの補完を効かせるために記述している
import { mdiPlusBoxMultipleOutline, mdiNoteEditOutline, mdiDeleteForeverOutline, mdiRefresh } from '@mdi/js'
import { useUserApi } from '@/composables/userApi';

const confirmDeletion = ref<any>(null)  // ConfirmDialogコンポーネントのref
const alert = ref<any>(null)  // Alertコンポーネントのref

definePageMeta({
  middleware: ["auth"]
})

// ユーザー一覧取得
const { data: users, pending, error: getUsersError, refresh: refreshUsers } = await useUserApi().getAll()

// アイテム一覧の取得に失敗した場合のエラー処理
onMounted(() => {
  if (getUsersError.value instanceof Error) {
    alert.value.error(getUsersError.value)
    console.error(getUsersError.value)
    return
  }
})

// アイテム削除
async function deleteUser(confirm: boolean, params: {id: number}) {
  if (!confirm) {
    return
  }
  const { error } = await useUserApi().delete(params.id)
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  refreshUsers()
}
</script>
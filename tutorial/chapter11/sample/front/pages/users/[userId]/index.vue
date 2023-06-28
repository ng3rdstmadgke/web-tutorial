<template>
  <div >
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">User (id={{ user?.id }})</div>
    </div>
    <div class="d-flex justify-end mb-3">
      <div class="mr-3">
        <v-btn :icon="mdiNoteEditOutline" color="warning" link :to="`/users/${user?.id}/edit`"></v-btn>
      </div>
      <div>
        <v-btn :icon="mdiDeleteForeverOutline" color="error" @click="confirmDeletion.open({id: user?.id})"></v-btn>
      </div>
    </div>
    <v-table>
      <thead>
        <tr>
          <th>Parameter</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>id</td>
          <td>{{ user?.id }}</td>
        </tr>
        <tr>
          <td>username</td>
          <td>{{ user?.username }}</td>
        </tr>
        <tr>
          <td>age</td>
          <td>{{ user?.age }}</td>
        </tr>
        <tr>
          <td>roles</td>
          <td>{{ user?.roles.map((r) => r.name).join(", ") }}</td>
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
import { mdiNoteEditOutline, mdiDeleteForeverOutline } from '@mdi/js'

// ミドルウェアによるログインチェック
definePageMeta({ middleware: ["auth"] })

// パスパラメータを取得
const {userId} = useRoute().params

const confirmDeletion = ref<any>(null)  // ConfirmDialogコンポーネントのref
const alert = ref<any>(null)  // Alertコンポーネントのref

// ユーザー取得
const { data: user, pending, error: getUserError, refresh } = await useUserApi().get(userId)

onMounted(() => {
  // ユーザー取得に失敗したらアラートを表示
  if (getUserError.value instanceof Error) {
    alert.value.error(getUserError.value)
    console.error(getUserError.value)
    return
  }
})

// アイテム削除
async function deleteUser(confirm: boolean, params: {id: number}) {
  // キャンセルされた場合は何もしない
  if (!confirm) { return }
  // 削除APIを呼び出す
  const { error } = await useUserApi().delete(params.id)
  // エラー: アラートを表示
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // 成功: ユーザー一覧ページに遷移
  useRouter().push({path: "/users/"})
}

</script>
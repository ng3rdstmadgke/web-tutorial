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

definePageMeta({
  middleware: ["auth"]
})

// パスパラメータを取得
const {userId} = useRoute().params

// テンプレートのref属性に指定した値を変数名としてrefオブジェクトを作成すると、テンプレートへの参照が作成される
// この参照を利用できるのは、テンプレートの描画が完了した後になる (onMountedないしはonUpdatedで利用)
// Template Refs: https://vuejs.org/guide/essentials/template-refs.html#accessing-the-refs
const confirmDeletion = ref<any>(null)  // ConfirmDialogコンポーネントのref
const alert = ref<any>(null)  // Alertコンポーネントのref


// ユーザー取得
const { data: user, pending, error: getUserError, refresh } = await useUserApi().get(userId)

onMounted(() => {
  if (getUserError.value instanceof Error) {
    alert.value.error(getUserError.value)
    console.error(getUserError.value)
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
  useRouter().push({path: "/users/"})
}

</script>
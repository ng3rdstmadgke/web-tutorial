<template>
  <div >
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">Item (id={{ item?.id }})</div>
    </div>
    <div class="d-flex justify-end mb-3">
      <div class="mr-3">
        <v-btn :icon="mdiNoteEditOutline" color="warning" link :to="`/items/${item?.id}/edit`"></v-btn>
      </div>
      <div>
        <v-btn :icon="mdiDeleteForeverOutline" color="error" @click="confirmDeletion.open({id: item?.id})"></v-btn>
      </div>
    </div>
    <v-card >
      <v-card-title>
        {{ item?.title }}
      </v-card-title>
      <v-card-text>
        {{ item?.content }}
      </v-card-text>
    </v-card>
    <ConfirmDialog
      title="アイテムの削除"
      message="本当に削除しますか"
      confirmBtn="削除"
      cancelBtn="キャンセル"
      colorCancel="primary"
      colorConfirm="error"
      ref="confirmDeletion"
      @confirm="deleteItem">
    </ConfirmDialog>
  </div>
</template>

<script setup lang="ts">
import { mdiNoteEditOutline, mdiDeleteForeverOutline } from '@mdi/js'

// ミドルウェアによる認証チェック
definePageMeta({
  middleware: ["auth"]
})

// パスパラメータ(itemId)を取得
const {itemId} = useRoute().params

const alert = ref<any>(null)  // Alertコンポーネントのref

// アイテム取得
const { data: item, pending, error: getItemError, refresh } = await useItemApi().get(itemId)

// アイテムの取得に失敗した場合のエラー処理
onMounted(() => {
  if (getItemError.value instanceof Error) {
    alert.value.error(getItemError.value)
    console.error(getItemError.value)
    return
  }
})

const confirmDeletion = ref<any>(null)  // ConfirmDialogコンポーネントの参照

// アイテム削除
async function deleteItem(confirm: boolean, params: {id: number}) {
  // 確認ダイアログで承認されたかをチェック
  if (!confirm) {
    return
  }
  // アイテム削除APIを呼び出し
  const { error } = await useItemApi().delete(params.id)
  // エラーの場合はアラートを表示
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  // 削除後はアイテム一覧画面に遷移
  useRouter().push({path: "/items/"})
}
</script>
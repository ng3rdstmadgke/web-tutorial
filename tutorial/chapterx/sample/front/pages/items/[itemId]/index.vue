<template>
  <div >
    <v-alert v-if="getError" dismissible type="error">{{ getError }}</v-alert>
    <v-alert v-model="deleteError" closable dismissible type="error">{{ deleteError }}</v-alert>
    <div class="mb-3">
      <div class="text-h4">Item (id={{ item.id }})</div>
    </div>
    <div class="d-flex justify-end mb-3">
      <div class="mr-3">
        <v-btn :icon="mdiNoteEditOutline" color="warning" link :to="`/items/${item.id}/edit`"></v-btn>
      </div>
      <div>
        <v-btn :icon="mdiDeleteForeverOutline" color="error" @click="confirmDeletion.open({id: item.id})"></v-btn>
      </div>
    </div>
    <v-card >
      <v-card-title>
        {{ item.title }}
      </v-card-title>
      <v-card-text>
        {{ item.content }}
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
import { mdiPlusBoxMultipleOutline, mdiNoteEditOutline, mdiDeleteForeverOutline, mdiRefresh } from '@mdi/js'

definePageMeta({
  middleware: ["auth"]
})

// パスパラメータを取得
const {itemId} = useRoute().params

// テンプレートのref属性に指定した値を変数名としてrefオブジェクトを作成すると、テンプレートへの参照が作成される
// この参照を利用できるのは、テンプレートの描画が完了した後になる (onMountedないしはonUpdatedで利用)
// Template Refs: https://vuejs.org/guide/essentials/template-refs.html#accessing-the-refs
const confirmDeletion = ref<any>(null)  // ConfirmDialogコンポーネントのref

// アイテム削除時のエラー
const deleteError = ref<Error | null>(null)


interface Item {
  id: number
  title: string
  content: string
}

// アイテム取得
const { data: item, pending, error: getError, refresh } = await useAsyncData<Item>(
  "getItem",
  () => {
    // サーバーサイドレンダリング時のURLは "http://" を付けないといけない
    return $fetch(`http://localhost:8018/api/v1/items/${itemId}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${useAuth().getToken()}`,
      },
    })
  },
)


// アイテム削除
async function deleteItem(confirm: boolean, params: {id: number}) {
  if (!confirm) {
    return
  }
  const { data , error } = await useAsyncData<any>(
    "deleteItem",
    () => {
      return $fetch(`//localhost:8018/api/v1/items/${params.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${useAuth().getToken()}`,
        },
      })
    }
  )
  if (error.value instanceof Error) {
    deleteError.value = error.value
    return
  }
  useRouter().push({path: "/items/"})
}

</script>
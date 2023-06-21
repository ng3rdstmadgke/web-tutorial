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
import { useItemApi } from '@/composables/itemApi';

definePageMeta({
  middleware: ["auth"]
})

// パスパラメータを取得
const {itemId} = useRoute().params

// テンプレートのref属性に指定した値を変数名としてrefオブジェクトを作成すると、テンプレートへの参照が作成される
// この参照を利用できるのは、テンプレートの描画が完了した後になる (onMountedないしはonUpdatedで利用)
// Template Refs: https://vuejs.org/guide/essentials/template-refs.html#accessing-the-refs
const confirmDeletion = ref<any>(null)  // ConfirmDialogコンポーネントのref
const alert = ref<any>(null)  // Alertコンポーネントのref


interface Item {
  id: number
  title: string
  content: string
}

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


// アイテム削除
async function deleteItem(confirm: boolean, params: {id: number}) {
  if (!confirm) {
    return
  }
  const { error } = await useItemApi().delete(params.id)
  if (error.value instanceof Error) {
    alert.value.error(error.value)
    console.error(error.value)
    return
  }
  useRouter().push({path: "/items/"})
}

</script>
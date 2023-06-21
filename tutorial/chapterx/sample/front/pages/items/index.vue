<template>
  <div>
    <Alert ref="alert" />
    <div class="mb-3">
      <div class="text-h4">Items</div>
    </div>
    <div class="d-flex justify-end">
      <div class="mr-3">
        <v-btn :icon="mdiRefresh" @click="refreshItems"></v-btn>
      </div>
      <div>
        <v-btn color="primary" :icon="mdiPlusBoxMultipleOutline" link to="/items/create"></v-btn>
      </div>
    </div>
    <v-table>
      <thead>
        <tr>
          <th>id</th>
          <th>title</th>
          <th>action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td><NuxtLink :to="`/items/${item.id}`">{{ item.id }}</NuxtLink></td>
          <td>{{ item.title }}</td>
          <td>
            <div class="d-flex">
              <div>
                <v-btn icon flat link :to="`/items/${item.id}/edit`">
                  <v-icon color="warning" :icon="mdiNoteEditOutline"></v-icon>
                </v-btn>
              </div>
              <div>
                <v-btn icon flat @click="confirmDeletion.open({id: item.id})">
                  <v-icon color="error" :icon="mdiDeleteForeverOutline"></v-icon>
                </v-btn>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </v-table>
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
// 明示的なインポートは不要だが、IDEの補完を効かせるために記述している
import { ref } from 'vue'
import { mdiPlusBoxMultipleOutline, mdiNoteEditOutline, mdiDeleteForeverOutline, mdiRefresh } from '@mdi/js'
import {useItemApi} from '@/composables/itemApi'

definePageMeta({
  middleware: ["auth"]
})


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

// アイテム一覧取得
const { data: items, pending, error: getItemsError, refresh: refreshItems } = await useItemApi().getAll()

// アイテム一覧の取得に失敗した場合のエラー処理
onMounted(() => {
  if (getItemsError.value instanceof Error) {
    alert.value.error(getItemsError.value)
    console.error(getItemsError.value)
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
  refreshItems()
}
</script>
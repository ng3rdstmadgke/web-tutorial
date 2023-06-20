<template>
  <div>
    <v-alert v-if="getError" dismissible type="error">{{ getError }}</v-alert>
    <v-alert v-model="deleteError" closable dismissible type="error">{{ deleteError }}</v-alert>
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

definePageMeta({
  middleware: ["auth"]
})


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

// アイテム一覧取得
const { data: items, pending, error: getError, refresh: refreshItems } = await useAsyncData<Item[]>(
  "getItems",
  () => {
    // サーバーサイドレンダリング時のURLは "http://" を付けないといけない
    return $fetch("http://localhost:8018/api/v1/items/", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${useAuth().getToken()}`,
      },
    })
  },
  //{ server: false, }
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
  refreshItems()
}

</script>
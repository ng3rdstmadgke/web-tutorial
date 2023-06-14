<template>
  <div>
    <div class="mb-3">
      <div class="text-h4">Items</div>
    </div>
    <v-table>
      <thead>
        <tr>
          <th>id</th>
          <th>title</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.title }}</td>
        </tr>
      </tbody>
    </v-table>
  </div>
</template>

<script setup lang="ts">
// 明示的なインポートは不要だが、IDEの補完を効かせるために記述している
import { ref } from 'vue'

definePageMeta({
  middleware: ["auth"]
})

interface Item {
  id: number
  title: string
  content: string
}

const { data: items, pending, error, refresh } = await useAsyncData<Item[]>(
  "getArticles",
  () => {
    return $fetch("//localhost:8018/api/v1/items/", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${useAuth().getToken()}`,
      },
    })
  }
)

</script>
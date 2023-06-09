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
        <tr v-for="article in articles" :key="article.id">
          <td>{{ article.id }}</td>
          <td>{{ article.title }}</td>
        </tr>
      </tbody>
    </v-table>
  </div>
</template>

<script setup lang="ts">
// 明示的なインポートは不要だが、IDEの補完を効かせるために記述している
import { ref } from 'vue'

interface Article {
  id: number
  title: string
}
const articles = ref<Article[]>([])
articles.value = [
  {
    id: 1,
    title: "Nuxt3入門",
  },
  {
    id: 2,
    title: "Jest再入門",
  },
]
</script>
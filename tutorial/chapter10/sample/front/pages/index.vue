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
          <th>action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.title }}</td>
          <td>
            <div class="d-flex">
              <div>
                <v-btn icon flat >
                  <v-icon color="warning" :icon="mdiNoteEditOutline"></v-icon>
                </v-btn>
              </div>
              <div>
                <v-btn icon flat >
                  <v-icon color="error" :icon="mdiDeleteForeverOutline"></v-icon>
                </v-btn>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </v-table>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ["auth"]
})

// refは明示的なインポートは不要だが、説明のために記述している
import { ref } from 'vue'
import { mdiNoteEditOutline, mdiDeleteForeverOutline } from '@mdi/js'

const items = ref<any>([
    {id: "1", "title": "Chapter1 FastAPI入門"},
    {id: "2", "title": "Chapter2 RDB入門"},
    {id: "3", "title": "Chapter2.5 SQLAlchemyを利用したデータベースの操作"},
    {id: "4", "title": "Chapter3 Alembicを利用したマイグレーションを実装してみよう"},
    {id: "5", "title": "Chapter4 FastAPIでCRUDを実装してみよう"},
])

</script>
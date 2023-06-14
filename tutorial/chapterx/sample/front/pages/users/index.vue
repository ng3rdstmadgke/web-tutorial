<template>
  <div>
    <div class="mb-3">
      <div class="text-h4">Users</div>
    </div>
    <v-table>
      <thead>
        <tr>
          <th>id</th>
          <th>username</th>
          <th>age</th>
          <th>roles</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.age }}</td>
          <td>{{ user.roles.map((e) => e.name).join(", ") }}</td>
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

interface User {
  id: number
  username: string
  age: number
  roles: {
    id: number
    name: string
  }[]
}

const { data: users, pending, error, refresh } = await useAsyncData<User[]>(
  "getArticles",
  () => {
    return $fetch("//localhost:8018/api/v1/users/", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${useAuth().getToken()}`,
      },
    })
  }
)
</script>
<template>
  <v-app id="inspire">
    <v-app-bar color="primary" :elevation="2">
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title>
        SampleApp
      </v-app-bar-title>
      <v-btn :icon="mdiLogout" @click="logout()"></v-btn>
    </v-app-bar>
    <v-navigation-drawer v-model="drawer">
      
      <v-sheet v-if="payload" color="grey-lighten-4" class="pa-4" >
        <v-avatar class="mb-4" color="accent" size="64" >{{ payload?.sub[0] }}</v-avatar>
        <div>{{ payload?.sub }}</div>
      </v-sheet>

      <v-divider></v-divider>

      <v-list>
        <v-list-item v-for="[icon, text, path] in links" :key="text" link :to="path">
          <template v-slot:prepend>
            <v-icon>{{ icon }}</v-icon>
          </template>
          <v-list-item-title>{{ text }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <v-container class="py-8 px-6" fluid >
        <slot />
      </v-container>
    </v-main>
    <v-footer>
      <div class="d-flex justify-center">
        <div>&copy; 2021</div>
      </div>
    </v-footer>
  </v-app>
</template>

<script setup lang="ts">
import { mdiAccount, mdiNote, mdiLogout, mdiLogin, mdiInformation } from '@mdi/js'

const drawer = ref<boolean>(true)
const links = ref<Array<[any, string, string]>>([
  [mdiInformation, 'top', "/"],
  [mdiLogin, 'Login', "/login"],
  [mdiNote, 'Item', "/items/"],
  [mdiAccount, 'User', "/users/"],
])


// login.vueはlayouts/default.vueの子コンポーネントなので、
// ログイン後に「ログインした」という情報がlayouts/default.vueに伝わらない。
// そのため、useStateを使ってlayouts/default.vueにログイン情報情報を伝える。
const payload = useState("tokenPayload")

function logout() {
  useAuth().logout()
  payload.value = null
  useRouter().push({path: "/login"})
}
</script>
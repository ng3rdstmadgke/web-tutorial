<template>
  <v-app id="inspire">
    <!-- ヘッダー >>> -->
    <v-app-bar color="primary" :elevation="2">
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title>
        <div @click="useRouter().push('/')" style="cursor: pointer;">SampleApp</div>
      </v-app-bar-title>
      <v-btn v-if="auth.authenticated()" :icon="mdiLogout" @click="logout()"></v-btn>
    </v-app-bar>
    <!-- <<< ヘッダー -->

    <!-- サイドメニュー >>> -->
    <v-navigation-drawer v-model="drawer">
      <!-- プロフィール -->
      <v-sheet color="grey-lighten-4" class="pa-4" >
        <v-avatar class="mb-4" color="accent" size="64" >SA</v-avatar>
        <div>sample.app</div>
      </v-sheet>
      <!-- プロフィール -->
      <v-divider></v-divider>
      <!-- メニューリスト >>> -->
      <v-list>
        <template v-for="item in menu" :key="item.name" >
          <v-list-item v-if="item.authenticated === auth.authenticated()" link :to="item.path">
            <template v-slot:prepend>
              <v-icon>{{ item.icon }}</v-icon>
            </template>
            <v-list-item-title>{{ item.name }}</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>
      <!-- メニューリスト >>> -->
    </v-navigation-drawer>
    <!-- <<< サイドメニュー -->

    <!-- コンテンツ >>> -->
    <v-main>
      <v-container class="py-8 px-6" fluid >
        <slot />
      </v-container>
    </v-main>
    <!-- <<< コンテンツ -->

    <!-- フッター >>> -->
    <v-footer class="footer justify-center">
      <div>&copy; 2023 Nuxt tutorial</div>
    </v-footer>
    <!-- <<< フッター -->
  </v-app>
</template>

<script setup lang="ts">
import { mdiAccount, mdiNote, mdiLogout, mdiLogin, mdiInformation } from '@mdi/js'

interface MenuItem {
  icon: string
  name: string
  path: string
  authenticated: boolean
}

const drawer = ref<boolean>(false)
const menu = ref<Array<MenuItem>>([
  {
    icon: mdiLogin,
    name: "Login",
    path: "/login",
    authenticated: false,
  },
  {
    icon: mdiNote,
    name: "Item",
    path: "/items/",
    authenticated: true,
  },
  {
    icon: mdiAccount,
    name: "User",
    path: "/users/",
    authenticated: true,
  },
])

const auth = useAuth()

function logout() {
  useAuth().logout()
  useRouter().push({path: "/login"})
}
</script>

<style lang="scss">
.footer {
  width: 100%;
  position: absolute;
  bottom: 0;
}
</style>

<template>
  <v-app id="inspire">
    <v-app-bar color="primary" :elevation="2">
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title>SampleApp</v-app-bar-title>
      <v-btn :icon="mdiLogout"></v-btn>
    </v-app-bar>
    <v-navigation-drawer v-model="drawer">
      <v-sheet color="grey-lighten-4" class="pa-4" >
        <v-avatar class="mb-4" color="accent" size="64" >John</v-avatar>
        <div>keita.midorikawa</div>
      </v-sheet>

      <v-divider></v-divider>

      <v-list>
        <v-list-item v-for="[icon, text] in links" :key="icon" link >
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
      <span>&copy; 2021</span>
    </v-footer>
  </v-app>
</template>

<script setup lang="ts">
import { mdiAccount, mdiNote, mdiLogout } from '@mdi/js'

const drawer = ref<boolean>(true)
const links = ref<Array<[any, string]>>([
  [mdiNote, 'Item'],
  [mdiAccount, 'User'],
])
</script>
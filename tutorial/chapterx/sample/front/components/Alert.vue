<template>
  <div>
    <v-alert
      v-model="show"
      :type="type"
      closable
      dismissible >{{ body }}</v-alert>
  </div>
</template>

<script setup lang="ts">
type AlertType = "error" | "success" | "info" | "warning"

const show = ref<boolean>(false)
const type = ref<AlertType>("error")
const body = ref<any>("")

function alert(
  alertType: AlertType,
  message: any,
) {
  show.value = true
  type.value = alertType
  body.value = message
}

function close() {
  show.value = false
}

defineExpose({ alert, close })
</script>
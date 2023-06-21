<template>
  <div style="position: relative">
    <div class="hp_alert_wrapper px-3">
      <div v-for="item in items">
        <v-alert
          class="mb-3"
          v-model="item.show"
          :type="item.type"
          closable
          dismissible >{{ item.body }}</v-alert>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
type AlertType = "error" | "success" | "info" | "warning"

const show = ref<boolean>(false)
const type = ref<AlertType>("error")
const body = ref<any>("")
interface AlertItem {
  show: boolean
  type: AlertType
  body: any
}

const items = ref<AlertItem[]>([])

function alert( alertType: AlertType, message: any) {
  items.value.push({
    show: true,
    type: alertType,
    body: message,
  })
}

defineExpose({
  error: (message: any) => alert("error", message),
  success: (message: any) => alert("success", message),
  info: (message: any) => alert("info", message),
  warning: (message: any) => alert("warning", message),
 })
</script>

<style>
.hp_alert_wrapper {
  z-index: 100;
  left: 0px;
  top: 0px;
  width: 100%;
  position: absolute;
}

</style>
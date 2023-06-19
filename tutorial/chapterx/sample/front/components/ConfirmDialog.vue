<template>
  <!--
    v-modelのdialogがtrueなら表示、falseなら非表示
    https://vuetifyjs.com/ja/components/dialogs/
  -->
  <v-dialog v-model="dialog" persistent max-width="400px">
    <v-card>
      <v-card-title>
        <span class="headline">{{props.title}}</span>
      </v-card-title>
      <v-card-text>
        {{props.message}}
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn :color="props.colorCancel"  @click="confirm(false)">{{cancelBtn}}</v-btn>
        <v-btn :color="props.colorConfirm" @click="confirm(true)">{{confirmBtn}}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
// ダイアログの表示・非表示のコントロール
const dialog = ref<boolean>(false)
// 親コンポーネントから受け取るパラメータ
let parameters: any = {}

// 親コンポーネントがダイアログを開くときに呼び出す関数
function open(v: any = {}) {
  dialog.value = true
  parameters = v
}

// ダイアログのボタンが押されたときに呼び出す関数
function confirm(confirm: boolean) {
  dialog.value = false
  emit("confirm", confirm, parameters)
}

interface Props {
  title: string
  message: string
  cancelBtn: string
  confirmBtn: string
  colorCancel: "primary" | "secondary" | "error" | "warning" | "info" | "success"
  colorConfirm: "primary" | "secondary" | "error" | "warning" | "info" | "success"
}


// propsはdefinePropsで定義する。デフォルト値はwithDefaultsで定義する。
// defineProps: https://vuejs.org/api/sfc-script-setup.html#defineprops-defineemits
const props = withDefaults(defineProps<Props>(), {
  title: "",
  message: "",
  cancelBtn: "Cancel",
  confirmBtn: "OK",
  colorCancel: "primary",
  colorConfirm: "error",
})

// イベントを発生させたいときは defineEmits を使う。
// defineEmits: https://vuejs.org/api/sfc-script-setup.html#defineprops-defineemits
const emit = defineEmits<{
  confirm: [ok: boolean, parameters: any], // named tuple syntax
}>()

// カスタムコンポーネント内の関数などを呼びたいときは defineExpose を使って、明示的に公開する必要がある。
// defineExpose: https://vuejs.org/api/sfc-script-setup.html#defineexpose
defineExpose({
  open: open,
})


</script>
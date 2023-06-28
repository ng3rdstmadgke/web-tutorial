// ミドルウェアは現在のルートをあらわす to と、遷移元のルートをあらわす from を引数に取ります。
export default defineNuxtRouteMiddleware((to, from) => {
  // 先ほど実装した Auth.authenticated を利用してログイン確認
  const auth = useAuth()
  if (!auth.authenticated()) {
    // 認証されていない場合はログインページにリダイレクト
    return navigateTo('/login')
  }
})
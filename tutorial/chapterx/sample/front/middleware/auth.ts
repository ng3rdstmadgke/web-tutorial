/**
 * ミドルウェアでは特定のルートに移動する前に実行したいコードを実装することができます。
 * https://nuxt.com/docs/guide/directory-structure/middleware
 *
 *
 * NuxtはnavigateTo()とabortNavigation() というミドルウェアのコールバック内でのみ利用可能な2つの関数を提供しています。
 * - navigateTo (to: RouteLocationRaw | undefined | null, options?: { replace: boolean, redirectCode: number, external: boolean )
 *   引数に渡したパスにリダイレクトします。
 * - abortNavigation (err?: string | Error)
 *   ナビゲーションを中止し、オプションのエラーメッセージを表示します。
 *
 * pageコンポーネント内でミドルウェアを利用する方法
 * ```
 * <script setup>
 * definePageMeta({
 *   middleware: ["auth"]
 *   // or middleware: 'auth'
 * })
 * </script>
 * ```
 */

// ミドルウェアは現在のルートをあらわす to と、遷移元のルートをあらわす from を引数に取ります。
export default defineNuxtRouteMiddleware((to, from) => {
  const auth = useAuth()
  if (!auth.authenticated()) {
    // 認証されていない場合はログインページにリダイレクト
    return navigateTo('/login')
  }
})
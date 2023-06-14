/**
 * utils/ 配下は自動でインポートされます(自動インポートの方法は composables/ 配下と同じです)
 * https://nuxt.com/docs/guide/directory-structure/utils
 * 
 * 
 * utils配下の実装方法
 * https://nuxt.com/docs/guide/directory-structure/composables#usage
 * 
 * ```utils/foo.ts
 * export const useFoo = () => {
 *   return {"bar": "piyo"}
 * }
 * ```
 * 
 * ```pages/index.vue
 * <template>
 *   <div>
 *     {{ foo.bar }}
 *   </div>
 * </template>
 * 
 * <script setup>
 * const foo = useFoo()
 * </script>
 * ```
 * 
 */
import { Buffer } from 'buffer'

export const useAuth = () => {
  return Auth
}

interface tokenPayload {
  sub: string
  scopes: string[]
  exp: number
}

class Auth {
  private static ACCESS_TOKEN_KEY: string = "__access_token"

  // 認証済みかどうかの判定
  public static authenticated(): boolean {
    let payload = this.getPayload()
    if (payload) {
      // トークンの有効期限を検証
      let now  = Math.floor((new Date()).getTime() / 1000)
      return payload.exp > now
    }
    return false
  }

  // CookieからJWTを削除
  public static logout(): void {
    const cookie = useCookie(this.ACCESS_TOKEN_KEY)
    cookie.value = null
  }

  // JWTをCookieに保存
  public static login(token: string): void {
    const cookie = useCookie(this.ACCESS_TOKEN_KEY)
    cookie.value = token
  }

  // Cookieに保存されているTokenのJWTのheaderをオブジェクト形式で取得する
  public static getHeader(): {[index: string]: any} | null {
    const cookie = useCookie(this.ACCESS_TOKEN_KEY)
    let token = cookie.value
    if (!token) return null
    let header = token.split(".")[0]
    let decoded = Buffer.from(header, "base64").toString()
    return JSON.parse(decoded)
  }

  // Cookieに保存されているTokenのJWTのpayloadをオブジェクト形式で取得する
  public static getPayload(): tokenPayload | null {
    const cookie = useCookie(this.ACCESS_TOKEN_KEY)
    let token = cookie.value
    if (!token) return null
    return Auth.parsePayload(token)
  }

  private static parsePayload(token: string): tokenPayload | null {
    let payload = token.split(".")[1]
    let decoded = Buffer.from(payload, "base64").toString()
    return JSON.parse(decoded)
  }

  public static getUsername(): string | null {
    let payload = Auth.getPayload();
    return (payload && !!payload.sub) ? payload.sub : null
  }

  public static hasPermission(required_permissions: string[]): boolean {
    let required_permission_set = new Set(required_permissions)
    let payload = this.getPayload();
    let scopes: string[] = (payload) ? payload["scopes"] : []
    // 積集合
    let actual = new Set(scopes.filter(x => required_permission_set.has(x)))
    return actual.size == required_permission_set.size
  }

}
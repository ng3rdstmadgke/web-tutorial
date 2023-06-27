import { Buffer } from 'buffer'

// Authクラスを返すuseAuthをエクスポートし外部から利用できるようにする
export const useAuth = () => {
  return Auth
}

interface tokenPayload {
  sub: string
  scopes: string[]
  exp: number
}

class Auth {
  // Cookieのキー
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

  // CookieからJWTを取得する
  public static getToken(): string | null {
    const cookie = useCookie(this.ACCESS_TOKEN_KEY);
    let token = cookie.value;
    return (token && Auth.authenticated()) ? token : null;
  }

  // Cookieに保存されているJWTのpayloadをオブジェクト形式で取得する
  public static getPayload(): tokenPayload | null {
    const cookie = useCookie(this.ACCESS_TOKEN_KEY)
    let token = cookie.value
    if (!token) return null
    let payload = token.split(".")[1]
    let decoded = Buffer.from(payload, "base64").toString()
    return JSON.parse(decoded)
  }

  // JWTのペイロードからユーザー名を取得する
  public static getUsername(): string | null {
    let payload = Auth.getPayload();
    return (payload && !!payload.sub) ? payload.sub : null
  }

  // JWTのペイロードのパーミッションに指定したパーミッションが含まれているかを判定する
  public static hasPermission(required_permissions: string[]): boolean {
    let required_permission_set = new Set(required_permissions)
    let payload = this.getPayload();
    let scopes: string[] = (payload) ? payload["scopes"] : []
    // 積集合
    let actual = new Set(scopes.filter(x => required_permission_set.has(x)))
    return actual.size == required_permission_set.size
  }
}
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE"
type QueryString = { [key: string]: string | number | boolean | string[] | number[] | boolean[] | null }
type Headers = { [key: string]: string }
type RequestBody = { [key: string]: any } | FormData

// ユーティリティを外部から利用できるように useApi() を公開
export const useApi = () => {
  return Api
}

class Api {
  // GETリクエストを送信するメソッド
  public static async get<T>( key: string, path: string, params: QueryString = {}, headers: Headers = {}) {
    // paramsをクエリパラメータの形式に変換する (例: {a: 1, b: 2} => "a=1&b=2")
    let query = Object.entries(params)
      .map(([k, v]) => {
        if (v instanceof Array) {
            return v.map((e) => `${k}=${encodeURIComponent(e)}`)
        } else {
            return `${k}=${encodeURIComponent(v ?? "")}`
        }
      })
      .flat()
      .join("&")
    let pathWithQuery = query.length > 0 ? `${path}?${query}` : path
    return Api.fetch<T>(key, "GET", pathWithQuery, null, headers)
  }

  // POSTリクエストを送信するメソッド
  public static async post<T>(key: string, path: string, params: RequestBody = {}, headers: Headers = {}) {
    let body = (params instanceof FormData) ? params : JSON.stringify(params)
    return Api.fetch<T>(key, "POST", path, body, headers)
  }

  // PUTリクエストを送信するメソッド
  public static async put<T>(key: string, path: string, params: RequestBody = {}, headers: Headers = {}) {
    let body = (params instanceof FormData) ? params : JSON.stringify(params)
    return Api.fetch<T>(key, "PUT", path, body, headers)
  }

  // DELETEリクエストを送信するメソッド
  public static async delete<T>(key: string, path: string, params: RequestBody = {}, headers: Headers = {}) {
    let body = (params instanceof FormData) ? params : JSON.stringify(params)
    return Api.fetch<T>(key, "DELETE", path, body, headers)
  }

  // APIリクエストを送信するメソッド
  private static async fetch<T>( key: string, method: HttpMethod, path: string, body: any, headers: Headers = {}) {
    const {clientBaseUrl, serverBaseUrl} = useRuntimeConfig().public;
    // RuntimeConfigに設定したベースURLを利用してクライアントサイドとサーバーサイドで宛先ホストを変更する
    // process.client で現在の実行環境がクライアントサイドかサーバーサイドかを判定できる
    const url = process.client ? `${clientBaseUrl}${path}` : `${serverBaseUrl}${path}`

    // 認証トークンを付与
    if (useAuth().authenticated()) {
      headers.Authorization = `Bearer ${useAuth().getToken()}`
    }

    // リクエスト送信
    return await useAsyncData<T>(
      key,
      () => {
        return $fetch(url, {
          method: method,
          headers: headers,
          body: body,
        })
      },
    )

  }
}
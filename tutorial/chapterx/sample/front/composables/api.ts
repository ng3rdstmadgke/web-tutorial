type HttpMethod = "GET" | "POST" | "PUT" | "DELETE"
type QueryString = { [key: string]: string | number | boolean | string[] | number[] | boolean[] | null }
type Headers = { [key: string]: string }
type RequestBody = { [key: string]: any } | FormData

export const useApi = () => {
  return Api
}

class Api {
  public static async get<T>( key: string, path: string, params: QueryString = {}, headers: Headers = {}) {
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

  public static async post<T>(key: string, path: string, params: RequestBody = {}, headers: Headers = {}) {
    let body = (params instanceof FormData) ? params : JSON.stringify(params)
    return Api.fetch<T>(key, "POST", path, body, headers)
  }

  public static async put<T>(key: string, path: string, params: RequestBody = {}, headers: Headers = {}) {
    let body = (params instanceof FormData) ? params : JSON.stringify(params)
    return Api.fetch<T>(key, "PUT", path, body, headers)
  }

  public static async delete<T>(key: string, path: string, params: RequestBody = {}, headers: Headers = {}) {
    let body = (params instanceof FormData) ? params : JSON.stringify(params)
    return Api.fetch<T>(key, "DELETE", path, body, headers)
  }

  private static async fetch<T>( key: string, method: HttpMethod, path: string, body: any, headers: Headers = {}) {
    const {clientBaseUrl, serverBaseUrl} = useRuntimeConfig().public;
    const url = process.client ? `${clientBaseUrl}${path}` : `${serverBaseUrl}${path}`

    if (useAuth().authenticated()) {
      headers.Authorization = `Bearer ${useAuth().getToken()}`
    }

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
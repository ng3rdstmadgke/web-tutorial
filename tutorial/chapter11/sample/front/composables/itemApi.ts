// リアイテム作成時のリクエストボディの型定義
interface ItemPost {
  title: string
  content: string
}

// アイテム更新時のリクエストボディの型定義
interface ItemPut {
  id: number
  title: string
  content: string
}

// アイテム取得時のレスポンスボディの型定義
interface ItemResponse {
  id: number
  title: string
  content: string
}

// useItemApiの名前で関数をエクスポート
export const useItemApi = () => {
  return {
    // アイテム一覧取得
    async getAll() {
      return useApi().get<ItemResponse[]>("getItems", "/items/")
    },
    // 指定したIDのアイテム取得
    async get(id: number) {
      return useApi().get<ItemResponse>("getItem", `/items/${id}`)
    },
    // アイテム作成
    async create(item: ItemPost) {
      return useApi().post<ItemResponse>("createItem", "/items/", item)
    },
    // アイテム更新
    async update(item: ItemPut) {
      return useApi().put<ItemResponse>("updateItem", `/items/${item.id}`, item)
    },
    // アイテム削除
    async delete(id: number) {
      return useApi().delete<any>("deleteItem", `/items/${id}`)
    }
  }
}
interface ItemPost {
  title: string
  content: string
}

interface ItemPut {
  id: number
  title: string
  content: string
}

interface ItemResponse {
  id: number
  title: string
  content: string
}

export const useItemApi = () => {
  return {
    async getAll() {
      return useApi().get<ItemResponse[]>("getItems", "/items/")
    },
    async get(id: number) {
      return useApi().get<ItemResponse>("getItem", `/items/${id}`)
    },
    async create(item: ItemPost) {
      return useApi().post<ItemResponse>("createItem", "/items/", item)
    },
    async update(item: ItemPut) {
      return useApi().put<ItemResponse>("updateItem", `/items/${item.id}`, item)
    },
    async delete(id: number) {
      return useApi().delete<any>("deleteItem", `/items/${id}`)
    }
  }
}
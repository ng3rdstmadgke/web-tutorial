
interface Item {
  id: number
  title: string
  content: string
}

interface ItemCreate {
  title: string
  content: string
}

export const useItemApi = () => {
  return {
    async getAll() {
      return useApi().get<Item[]>("getItems", "/items/")
    },
    async get(id: number) {
      return useApi().get<Item>("getItem", `/items/${id}`)
    },
    async create(item: ItemCreate) {
      return useApi().post<Item>("createItem", "/items/", item)
    },
    async update(item: Item) {
      return useApi().put<Item>("updateItem", `/items/${item.id}`, item)
    },
    async delete(id: number) {
      return useApi().delete<any>("deleteItem", `/items/${id}`)
    }
  }
}
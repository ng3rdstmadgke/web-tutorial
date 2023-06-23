
interface UserPost {
  username: string
  password: string
  age: number
  role_ids: number[]
}

interface UserPut {
  id: number
  password: string
  age: number
  role_ids: number[]
}

interface UserResponse {
  id: number
  username: string
  age: number
  roles: {
    id: number,
    name: string
  }[]
}

export const useUserApi = () => {
  return {
    async getAll() {
      return useApi().get<UserResponse[]>("getUsers", "/users/")
    },
    async get(id: number) {
      return useApi().get<UserResponse>("getUser", `/users/${id}`)
    },
    async create(user: UserPost) {
      return useApi().post<UserResponse>("createUser", "/users/", user)
    },
    async update(user: UserPut) {
      return useApi().put<UserResponse>("updateUser", `/users/${user.id}`, user)
    },
    async delete(id: number) {
      return useApi().delete<any>("deleteUser", `/users/${id}`)
    }
  }
}
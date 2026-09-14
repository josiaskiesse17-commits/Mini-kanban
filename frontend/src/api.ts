export type Priority = 'low' | 'medium' | 'high'

export type User = {
  id: number
  username: string
  created_at: string
}

export type Card = {
  id: number
  column_id: number
  title: string
  description: string
  priority: Priority
  due_date: string | null
  position: number
  created_at: string
  updated_at: string
}

export type Column = {
  id: number
  board_id: number
  name: string
  position: number
  cards: Card[]
}

export type Board = {
  id: number
  name: string
  user_id: number
  created_at: string
  updated_at: string
  columns: Column[]
}

export type AuthResponse = {
  access_token: string
  token_type: 'bearer'
  user: User
}

export type ApiError = {
  detail: string | Array<{ loc: string[]; msg: string; type: string }>
}

export class ApiRequestError extends Error {
  status: number
  detail: ApiError['detail']

  constructor(status: number, detail: ApiError['detail']) {
    super(typeof detail === 'string' ? detail : 'Request validation failed')
    this.name = 'ApiRequestError'
    this.status = status
    this.detail = detail
  }
}

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'
const TOKEN_KEY = 'mini-kanban-token'

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Content-Type', 'application/json')
  const token = tokenStore.get()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const response = await fetch(`${API_URL}${path}`, { ...init, headers })
  if (!response.ok) {
    const body = (await response.json().catch(() => ({ detail: response.statusText }))) as ApiError
    throw new ApiRequestError(response.status, body.detail)
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

export const api = {
  register: async (username: string, password: string) => {
    const result = await request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    tokenStore.set(result.access_token)
    return result
  },
  login: async (username: string, password: string) => {
    const result = await request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    tokenStore.set(result.access_token)
    return result
  },
  logout: async () => {
    try {
      await request<void>('/auth/logout', { method: 'POST' })
    } finally {
      tokenStore.clear()
    }
  },
  listBoards: () => request<Board[]>('/boards'),
  getBoard: (boardId: number) => request<Board>(`/boards/${boardId}`),
  createBoard: (name: string) => request<Board>('/boards', {
    method: 'POST',
    body: JSON.stringify({ name }),
  }),
  updateBoard: (boardId: number, name: string) => request<Board>(`/boards/${boardId}`, {
    method: 'PATCH',
    body: JSON.stringify({ name }),
  }),
  deleteBoard: (boardId: number) => request<void>(`/boards/${boardId}`, { method: 'DELETE' }),
  reorderColumns: (boardId: number, ids: number[]) => request<Column[]>(`/boards/${boardId}/columns/reorder`, {
    method: 'PUT',
    body: JSON.stringify({ ids }),
  }),
  createColumn: (boardId: number, name: string) => request<Column>(`/boards/${boardId}/columns`, {
    method: 'POST',
    body: JSON.stringify({ name }),
  }),
  updateColumn: (columnId: number, name: string) => request<Column>(`/columns/${columnId}`, {
    method: 'PATCH',
    body: JSON.stringify({ name }),
  }),
  deleteColumn: (columnId: number) => request<void>(`/columns/${columnId}`, { method: 'DELETE' }),
  createCard: (columnId: number, card: Partial<Pick<Card, 'title' | 'description' | 'priority' | 'due_date' | 'position'>>) =>
    request<Card>(`/columns/${columnId}/cards`, { method: 'POST', body: JSON.stringify(card) }),
  updateCard: (cardId: number, card: Partial<Pick<Card, 'title' | 'description' | 'priority' | 'due_date' | 'position'>>) =>
    request<Card>(`/cards/${cardId}`, { method: 'PATCH', body: JSON.stringify(card) }),
  deleteCard: (cardId: number) => request<void>(`/cards/${cardId}`, { method: 'DELETE' }),
  moveCard: (cardId: number, columnId: number, position: number) =>
    request<Card>(`/cards/${cardId}/move`, {
      method: 'POST',
      body: JSON.stringify({ column_id: columnId, position }),
    }),
}

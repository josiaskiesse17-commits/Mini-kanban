import { useEffect, useState } from 'react'
import type { DragEvent, FormEvent } from 'react'
import './App.css'
import { ApiRequestError, api, tokenStore } from './api'
import type { Board, Card, Priority, User } from './api'

type Mode = 'login' | 'register'
type Theme = 'light' | 'dark'

function ThemeToggle({ theme, onToggle }: { theme: Theme; onToggle: () => void }) {
  const nextTheme = theme === 'light' ? 'dark' : 'light'
  return <button className="button button-quiet theme-toggle" type="button" onClick={onToggle} aria-label={`Switch to ${nextTheme} theme`} title={`Switch to ${nextTheme} theme`}>
    <span aria-hidden="true">{theme === 'light' ? '☾' : '☼'}</span>
  </button>
}

function App() {
  const [theme, setTheme] = useState<Theme>(() => localStorage.getItem('mini-kanban-theme') === 'dark' ? 'dark' : 'light')
  const [authenticated, setAuthenticated] = useState(() => Boolean(tokenStore.get()))
  const [user, setUser] = useState<User | null>(null)
  const [boards, setBoards] = useState<Board[]>([])
  const [mode, setMode] = useState<Mode>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [boardsLoading, setBoardsLoading] = useState(() => Boolean(tokenStore.get()))
  const [boardName, setBoardName] = useState('')
  const [editingBoardId, setEditingBoardId] = useState<number | null>(null)
  const [editingName, setEditingName] = useState('')
  const [activeBoard, setActiveBoard] = useState<Board | null>(null)
  const [columnName, setColumnName] = useState('')
  const [editingColumnId, setEditingColumnId] = useState<number | null>(null)
  const [editingColumnName, setEditingColumnName] = useState('')
  const [newCardTitle, setNewCardTitle] = useState('')
  const [newCardDescription, setNewCardDescription] = useState('')
  const [newCardPriority, setNewCardPriority] = useState<Priority>('medium')
  const [newCardDueDate, setNewCardDueDate] = useState('')
  const [editingCardId, setEditingCardId] = useState<number | null>(null)
  const [editingCardTitle, setEditingCardTitle] = useState('')
  const [editingCardDescription, setEditingCardDescription] = useState('')
  const [editingCardPriority, setEditingCardPriority] = useState<Priority>('medium')
  const [editingCardDueDate, setEditingCardDueDate] = useState('')
  const [draggingCardId, setDraggingCardId] = useState<number | null>(null)
  const [cardSearch, setCardSearch] = useState('')
  const [priorityFilter, setPriorityFilter] = useState<Priority | 'all'>('all')

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('mini-kanban-theme', theme)
  }, [theme])

  useEffect(() => {
    if (!tokenStore.get()) return
    api.listBoards().then(setBoards).catch(() => {
      tokenStore.clear()
      setAuthenticated(false)
      setError('Your session has expired. Please log in again.')
    }).finally(() => setBoardsLoading(false))
  }, [])

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const result = mode === 'login'
        ? await api.login(username, password)
        : await api.register(username, password)
      setAuthenticated(true)
      setUser(result.user)
      setBoards(await api.listBoards())
      setPassword('')
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to connect to the API')
    } finally {
      setLoading(false)
    }
  }

  async function logout() {
    await api.logout()
    setAuthenticated(false)
    setUser(null)
    setBoards([])
  }

  async function createBoard(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!boardName.trim()) return
    setLoading(true)
    setError('')
    try {
      const board = await api.createBoard(boardName.trim())
      setBoards((current) => [...current, board])
      setBoardName('')
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to create board')
    } finally {
      setLoading(false)
    }
  }

  async function renameBoard(boardId: number) {
    if (!editingName.trim()) return
    try {
      const board = await api.updateBoard(boardId, editingName.trim())
      setBoards((current) => current.map((item) => item.id === boardId ? board : item))
      setEditingBoardId(null)
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to rename board')
    }
  }

  async function deleteBoard(board: Board) {
    if (!window.confirm(`Delete ${board.name}?`)) return
    try {
      await api.deleteBoard(board.id)
      setBoards((current) => current.filter((item) => item.id !== board.id))
      if (activeBoard?.id === board.id) setActiveBoard(null)
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to delete board')
    }
  }

  async function openBoard(board: Board) {
    setError('')
    try {
      setActiveBoard(await api.getBoard(board.id))
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to open board')
    }
  }

  async function moveColumn(board: Board, index: number, direction: -1 | 1) {
    const target = index + direction
    if (target < 0 || target >= board.columns.length) return
    const columns = [...board.columns]
    ;[columns[index], columns[target]] = [columns[target], columns[index]]
    try {
      const saved = await api.reorderColumns(board.id, columns.map((column) => column.id))
      setActiveBoard({ ...board, columns: saved })
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to reorder columns')
    }
  }

  async function createColumn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!activeBoard || !columnName.trim()) return
    try {
      const column = await api.createColumn(activeBoard.id, columnName.trim())
      setActiveBoard({ ...activeBoard, columns: [...activeBoard.columns, column] })
      setColumnName('')
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to create column')
    }
  }

  async function renameColumn(columnId: number) {
    if (!activeBoard || !editingColumnName.trim()) return
    try {
      const column = await api.updateColumn(columnId, editingColumnName.trim())
      setActiveBoard({ ...activeBoard, columns: activeBoard.columns.map((item) => item.id === columnId ? { ...item, name: column.name } : item) })
      setEditingColumnId(null)
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to rename column')
    }
  }

  async function deleteColumn(columnId: number, name: string) {
    if (!activeBoard || !window.confirm(`Delete ${name}?`)) return
    try {
      await api.deleteColumn(columnId)
      setActiveBoard({ ...activeBoard, columns: activeBoard.columns.filter((item) => item.id !== columnId) })
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to delete column')
    }
  }

  async function createCard(event: FormEvent<HTMLFormElement>, columnId: number) {
    event.preventDefault()
    if (!activeBoard || !newCardTitle.trim()) return
    try {
      await api.createCard(columnId, {
        title: newCardTitle.trim(),
        description: newCardDescription,
        priority: newCardPriority,
        due_date: newCardDueDate || null,
      })
      setActiveBoard(await api.getBoard(activeBoard.id))
      setNewCardTitle('')
      setNewCardDescription('')
      setNewCardPriority('medium')
      setNewCardDueDate('')
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to create card')
    }
  }

  function startEditingCard(card: Card) {
    setEditingCardId(card.id)
    setEditingCardTitle(card.title)
    setEditingCardDescription(card.description)
    setEditingCardPriority(card.priority)
    setEditingCardDueDate(card.due_date ?? '')
  }

  async function saveCard(cardId: number) {
    if (!activeBoard || !editingCardTitle.trim()) return
    try {
      await api.updateCard(cardId, {
        title: editingCardTitle.trim(),
        description: editingCardDescription,
        priority: editingCardPriority,
        due_date: editingCardDueDate || null,
      })
      setActiveBoard(await api.getBoard(activeBoard.id))
      setEditingCardId(null)
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to update card')
    }
  }

  async function deleteCard(card: Card) {
    if (!activeBoard || !window.confirm(`Delete ${card.title}?`)) return
    try {
      await api.deleteCard(card.id)
      setActiveBoard(await api.getBoard(activeBoard.id))
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to delete card')
    }
  }

  function startDragging(event: DragEvent<HTMLElement>, cardId: number) {
    event.dataTransfer.setData('text/plain', String(cardId))
    event.dataTransfer.effectAllowed = 'move'
    setDraggingCardId(cardId)
  }

  async function dropCard(event: DragEvent<HTMLElement>, columnId: number, position: number) {
    event.preventDefault()
    event.stopPropagation()
    const cardId = Number(event.dataTransfer.getData('text/plain'))
    if (!cardId || !activeBoard) return
    try {
      await api.moveCard(cardId, columnId, position)
      setActiveBoard(await api.getBoard(activeBoard.id))
    } catch (reason) {
      setError(reason instanceof ApiRequestError ? reason.message : 'Unable to move card')
    } finally {
      setDraggingCardId(null)
    }
  }

  if (authenticated) {
    return (
      <main className="app-shell">
        <header className="topbar">
          <div><span className="eyebrow">MINI KANBAN</span><h1>{activeBoard?.name ?? 'Workspace'}</h1></div>
          <div className="topbar-actions">
            <ThemeToggle theme={theme} onToggle={() => setTheme(theme === 'light' ? 'dark' : 'light')} />
            {activeBoard && <button className="button button-quiet" type="button" onClick={() => setActiveBoard(null)}>All boards</button>}
            <button className="button button-quiet" type="button" onClick={logout}>Log out</button>
          </div>
        </header>
        {activeBoard ? (
          <section className="kanban-board">
            <div className="board-heading"><div><p className="eyebrow">BOARD VIEW</p><h2>{activeBoard.name}</h2></div><span className="muted">{activeBoard.columns.length} columns</span></div>
            <div className="board-filters">
              <input aria-label="Search cards" placeholder="Search cards" value={cardSearch} onChange={(event) => setCardSearch(event.target.value)} />
              <select aria-label="Filter by priority" value={priorityFilter} onChange={(event) => setPriorityFilter(event.target.value as Priority | 'all')}><option value="all">All priorities</option><option value="low">Low priority</option><option value="medium">Medium priority</option><option value="high">High priority</option></select>
            </div>
            <form className="create-column" onSubmit={createColumn}>
              <input aria-label="New column name" placeholder="Add a column" value={columnName} onChange={(event) => setColumnName(event.target.value)} />
              <button className="button button-primary" type="submit">Add column</button>
            </form>
            {error && <p className="error" role="alert">{error}</p>}
            <div className="kanban-columns">
              {activeBoard.columns.map((column, index) => (
                <section className="kanban-column" key={column.id} onDragOver={(event) => event.preventDefault()} onDrop={(event) => void dropCard(event, column.id, column.cards.length)}>
                  <header className="column-heading">
                    {editingColumnId === column.id ? <input autoFocus value={editingColumnName} onChange={(event) => setEditingColumnName(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && void renameColumn(column.id)} /> : <h3>{column.name}</h3>}
                    <div className="column-actions">
                      <button className="text-button" disabled={index === 0} type="button" aria-label={`Move ${column.name} left`} onClick={() => void moveColumn(activeBoard, index, -1)}>←</button>
                      <button className="text-button" disabled={index === activeBoard.columns.length - 1} type="button" aria-label={`Move ${column.name} right`} onClick={() => void moveColumn(activeBoard, index, 1)}>→</button>
                      {editingColumnId === column.id ? <button className="text-button" type="button" onClick={() => void renameColumn(column.id)}>Save</button> : <button className="text-button" type="button" onClick={() => { setEditingColumnId(column.id); setEditingColumnName(column.name) }}>Rename</button>}
                      <button className="text-button danger" type="button" onClick={() => void deleteColumn(column.id, column.name)}>Delete</button>
                    </div>
                  </header>
                  <form className="new-card-form" onSubmit={(event) => void createCard(event, column.id)}>
                    <input aria-label={`New card title for ${column.name}`} placeholder="New card title" value={newCardTitle} onChange={(event) => setNewCardTitle(event.target.value)} />
                    <button className="text-button" type="submit">+ Add card</button>
                  </form>
                  <div className="card-list">
                    {column.cards.filter((card) => card.title.toLowerCase().includes(cardSearch.toLowerCase()) && (priorityFilter === 'all' || card.priority === priorityFilter)).length === 0 ? <p className="muted empty-column">No matching cards</p> : column.cards.filter((card) => card.title.toLowerCase().includes(cardSearch.toLowerCase()) && (priorityFilter === 'all' || card.priority === priorityFilter)).map((card) => (
                      <article className={`task-card ${draggingCardId === card.id ? 'is-dragging' : ''}`} draggable onDragStart={(event) => startDragging(event, card.id)} onDragEnd={() => setDraggingCardId(null)} onDragOver={(event) => event.preventDefault()} onDrop={(event) => void dropCard(event, column.id, column.cards.indexOf(card))} key={card.id}>
                        {editingCardId === card.id ? (
                          <form className="edit-card-form" onSubmit={(event) => { event.preventDefault(); void saveCard(card.id) }}>
                            <input aria-label="Card title" value={editingCardTitle} onChange={(event) => setEditingCardTitle(event.target.value)} />
                            <textarea aria-label="Card description" value={editingCardDescription} onChange={(event) => setEditingCardDescription(event.target.value)} />
                            <div className="card-fields"><select aria-label="Card priority" value={editingCardPriority} onChange={(event) => setEditingCardPriority(event.target.value as Priority)}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select><input aria-label="Card due date" type="date" value={editingCardDueDate} onChange={(event) => setEditingCardDueDate(event.target.value)} /></div>
                            <div className="card-actions"><button className="text-button" type="submit">Save</button><button className="text-button" type="button" onClick={() => setEditingCardId(null)}>Cancel</button></div>
                          </form>
                        ) : <><h4>{card.title}</h4><p>{card.description}</p><div className="card-actions"><button className="text-button" type="button" onClick={() => startEditingCard(card)}>Edit</button><button className="text-button danger" type="button" onClick={() => void deleteCard(card)}>Delete</button></div></>}
                        <footer><span className={`priority priority-${card.priority}`}>{card.priority}</span>{card.due_date && <time dateTime={card.due_date}>Due {card.due_date}</time>}</footer>
                      </article>
                    ))}
                  </div>
                </section>
              ))}
            </div>
          </section>
        ) : (
        <section className="workspace-panel">
          <p className="eyebrow">PRIVATE BOARDS</p>
          <h2>{user ? `Welcome back, ${user.username}` : 'Your workspace'}</h2>
          <form className="create-board" onSubmit={createBoard}>
            <input aria-label="New board name" placeholder="Name a new board" value={boardName} onChange={(event) => setBoardName(event.target.value)} />
            <button className="button button-primary" disabled={loading} type="submit">Add board</button>
          </form>
          {error && <p className="error" role="alert">{error}</p>}
          {boardsLoading ? <p className="muted">Loading boards...</p> : boards.length === 0 ? (
            <p className="empty-state">No boards yet. Create your first one above.</p>
          ) : (
            <div className="board-list">
              {boards.map((board) => (
                <article className="board-row" key={board.id}>
                  {editingBoardId === board.id ? (
                    <input autoFocus value={editingName} onChange={(event) => setEditingName(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && void renameBoard(board.id)} />
                  ) : <h3>{board.name}</h3>}
                  <button className="text-button open-board" type="button" onClick={() => void openBoard(board)}>Open board</button>
                  <div className="board-actions">
                    {editingBoardId === board.id ? <button className="text-button" type="button" onClick={() => void renameBoard(board.id)}>Save</button> : <button className="text-button" type="button" onClick={() => { setEditingBoardId(board.id); setEditingName(board.name) }}>Rename</button>}
                    <button className="text-button danger" type="button" onClick={() => void deleteBoard(board)}>Delete</button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
        )}
      </main>
    )
  }

  return (
    <main className="auth-layout">
      <ThemeToggle theme={theme} onToggle={() => setTheme(theme === 'light' ? 'dark' : 'light')} />
      <section className="auth-intro">
        <span className="eyebrow">MINI KANBAN / 01</span>
        <h1>Make the work visible.</h1>
        <p>A quiet place for clear priorities, honest progress, and finished work.</p>
      </section>
      <section className="auth-panel" aria-labelledby="auth-title">
        <div className="mode-switch" role="tablist" aria-label="Authentication mode">
          <button className={mode === 'login' ? 'active' : ''} type="button" onClick={() => setMode('login')}>Log in</button>
          <button className={mode === 'register' ? 'active' : ''} type="button" onClick={() => setMode('register')}>Register</button>
        </div>
        <h2 id="auth-title">{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
        <p className="muted">{mode === 'login' ? 'Sign in to continue to your boards.' : 'Start organizing your next clear win.'}</p>
        <form onSubmit={submit}>
          <label>Username<input required minLength={3} value={username} onChange={(event) => setUsername(event.target.value)} /></label>
          <label>Password<input required minLength={8} type="password" value={password} onChange={(event) => setPassword(event.target.value)} /></label>
          {error && <p className="error" role="alert">{error}</p>}
          <button className="button button-primary" disabled={loading} type="submit">{loading ? 'Working...' : mode === 'login' ? 'Enter workspace' : 'Create account'}</button>
        </form>
      </section>
    </main>
  )
}

export default App

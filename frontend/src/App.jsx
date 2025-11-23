import { useState, useEffect } from 'react'
import './App.css'

function App() {
    const [tasks, setTasks] = useState([])
    const [name, setName] = useState('')
    const [time_limit, setTimeLimit] = useState('')
    const [editableTaskId, setEditableTaskId] = useState(null)

    const fetchTasks = () => {
        fetch('http://127.0.0.1:8000/tasks/')
        .then(res => res.json())
        .then(data => setTasks(data))
        .catch(err => console.error(err))
    }

    useEffect(() => {
        fetchTasks()
    }, [])

    const handleSubmit = () => {
        const taskData = {name: name, time_limit: time_limit}

        if (editableTaskId) {
            fetch(`http://127.0.0.1:8000/tasks/${editableTaskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify(taskData)
        }).then(() => {
            fetchTasks()
            resetForm()
        })}
        else {
            fetch("http://127.0.0.1:8000/tasks/", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(taskData)
            }).then(() => {
                fetchTasks()
                resetForm()
            })
        }
    }



    const handleDelete = (id) => {
        fetch(`http://127.0.0.1:8000/tasks/${id}`, {
        method: 'DELETE'
        })
        .then(() => {
            fetchTasks()
        })
    }

    const startEdit = (task) => {
        setEditableTaskId(task.id)
        setName(task.name)
        setTimeLimit(task.time_limit)
    }
    const resetForm = () => {
        setEditableTaskId(null)
        setName('')
        setTimeLimit('')
    }

    return (
        <div style={{ maxWidth: '600px', margin: '0 auto'}}>
            <h1>To-Do List 🚀</h1>

            <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #444', borderRadius: '8px'}}>
                <h2>{editableTaskId ? 'Редактировать задачу' : 'Новая задача'}</h2>

                <input
                  placeholder="Название задачи"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  style={{ marginRight: '10px', padding: '8px'}}
                />
                <input
                  placeholder="Срок"
                  value={time_limit}
                  onChange={e => setTimeLimit(e.target.value)}
                  style={{ marginRight: '10px', padding: '8px'}}
                />
                <button onClick={handleSubmit}>
                    {editableTaskId ? 'Сохранить' : 'Добавить'}
                </button>

                {editableTaskId && (
                    <button onClick={resetForm} style={{marginRight: '10px', background: 'gray'}}>
                        Отмена
                    </button>
                )}
            </div>
            <div>
                {tasks.map(task => (
                    <div key={task.id} style={{
                        background:'#2a2a2a',
                        padding: '15px',
                        margin: '10px 0',
                        borderRadius: '8px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'}}>
                        <div style={{ textAlign: 'left'}}>
                            <div style={{ fontSize: '1.2em', fontWeight:'bold', color: 'white'}}>{task.name}</div>
                            <div style={{ color: '#888' }}>Дедлайн: {task.time_limit}</div>
                        </div>
                        <div>
                            <button onClick={() => startEdit(task)}
                                style={{marginRight: '10px', background: '#007bff'}}
                            >
                            Отредактировать
                            </button>
                            <button onClick={() => handleDelete(task.id)}
                                style={{ background: '#dc3545' }}
                            >
                            Удалить
                            </button>
                        </div>
                    </div>
                    ))
                }
            </div>

        </div>
    )
}
export default App
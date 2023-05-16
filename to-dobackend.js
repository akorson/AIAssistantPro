const express = require('express')
const bodyParser = require('body-parser')
const cors = require('cors')
const Task = require('./models/task')
const AI = require('./ai')

const app = express()
app.use(cors())
app.use(bodyParser.json())

// Store tasks in memory (can be replaced with a database)
const tasks = []

// Endpoint to create a new task
app.post('/api/tasks', (req, res) => {
  const { title, description, dueDate } = req.body

  const task = new Task(title, description, dueDate)
  tasks.push(task)

  res.status(201).json({ message: 'Task created successfully' })
})

// Endpoint to get all tasks
app.get('/api/tasks', (req, res) => {
  res.json(tasks)
})

// Endpoint to get a specific task by ID
app.get('/api/tasks/:id', (req, res) => {
  const taskId = req.params.id
  const task = tasks.find((task) => task.id === taskId)

  if (!task) {
    return res.status(404).json({ message: 'Task not found' })
  }

  res.json(task)
})

// Endpoint to mark a task as completed
app.patch('/api/tasks/:id/complete', (req, res) => {
  const taskId = req.params.id
  const task = tasks.find((task) => task.id === taskId)

  if (!task) {
    return res.status(404).json({ message: 'Task not found' })
  }

  task.complete()
  res.json({ message: 'Task completed successfully' })
})

// Endpoint to get AI suggestions for task completion
app.get('/api/tasks/:id/suggestions', (req, res) => {
  const taskId = req.params.id
  const task = tasks.find((task) => task.id === taskId)

  if (!task) {
    return res.status(404).json({ message: 'Task not found' })
  }

  const suggestions = AI.generateSuggestions(task)
  res.json(suggestions)
})

// Endpoint to prioritize a task
app.patch('/api/tasks/:id/prioritize', (req, res) => {
  const taskId = req.params.id
  const task = tasks.find((task) => task.id === taskId)

  if (!task) {
    return res.status(404).json({ message: 'Task not found' })
  }

  const { priority } = req.body
  task.setPriority(priority)

  res.json({ message: 'Task prioritized successfully' })
})

// Start the server
const port = process.env.PORT || 3000
app.listen(port, () => {
  console.log(`Server is running on port ${port}`)
})

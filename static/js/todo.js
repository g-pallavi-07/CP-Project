document.addEventListener('DOMContentLoaded', () => {
  const addTodoBtn = document.getElementById('add-todo-btn');
  const popup = document.getElementById('todo-popup');
  const saveTodoBtn = document.getElementById('save-todo-btn');
  const cancelTodoBtn = document.getElementById('cancel-todo-btn');
  const todoInput = document.getElementById('todo-input');
  const todoList = document.getElementById('todo-list');

  // Load todos on start
  fetch('/get_todos')
    .then(res => res.json())
    .then(data => {
      todoList.innerHTML = '';
      data.forEach(todo => {
        addTodoToDOM(todo);
      });
    });

  // Show popup
  addTodoBtn.addEventListener('click', () => {
    popup.classList.remove('hidden');
    todoInput.value = '';
    todoInput.focus();
  });

  // Hide popup
  cancelTodoBtn.addEventListener('click', () => {
    popup.classList.add('hidden');
  });

// save new todo
  saveTodoBtn.addEventListener('click', () => {
    popup.classList.add('hidden');
  });
})
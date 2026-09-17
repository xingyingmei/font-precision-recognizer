(() => {
  'use strict';

  const STORAGE_KEY = 'font-precision-recognizer.todos.v1';
  const form = document.querySelector('#todo-form');
  const input = document.querySelector('#todo-input');
  const list = document.querySelector('#todo-list');
  const emptyState = document.querySelector('#empty-state');
  const count = document.querySelector('#todo-count');
  const clearCompleted = document.querySelector('#clear-completed');
  const filterButtons = [...document.querySelectorAll('[data-filter]')];

  let todos = loadTodos();
  let currentFilter = 'all';

  function loadTodos() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      return Array.isArray(saved) ? saved.filter(todo => todo && todo.id && todo.text) : [];
    } catch (error) {
      console.warn('Could not load saved todos:', error);
      return [];
    }
  }

  function saveTodos() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
  }

  function visibleTodos() {
    if (currentFilter === 'active') return todos.filter(todo => !todo.completed);
    if (currentFilter === 'completed') return todos.filter(todo => todo.completed);
    return todos;
  }

  function render() {
    const visible = visibleTodos();
    list.replaceChildren();
    emptyState.hidden = visible.length !== 0;

    visible.forEach(todo => {
      const item = document.createElement('li');
      item.className = `todo-item${todo.completed ? ' completed' : ''}`;
      item.dataset.id = todo.id;

      const label = document.createElement('label');
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = todo.completed;
      checkbox.setAttribute('aria-label', `Mark ${todo.text} as complete`);
      checkbox.addEventListener('change', () => toggleTodo(todo.id));

      const text = document.createElement('span');
      text.className = 'todo-text';
      text.textContent = todo.text;
      label.append(checkbox, text);

      const deleteButton = document.createElement('button');
      deleteButton.className = 'delete-task';
      deleteButton.type = 'button';
      deleteButton.textContent = '×';
      deleteButton.title = 'Delete task';
      deleteButton.setAttribute('aria-label', `Delete ${todo.text}`);
      deleteButton.addEventListener('click', () => deleteTodo(todo.id));

      item.append(label, deleteButton);
      list.append(item);
    });

    const remaining = todos.filter(todo => !todo.completed).length;
    count.textContent = `${remaining} ${remaining === 1 ? 'task' : 'tasks'} left`;
    filterButtons.forEach(button => {
      const active = button.dataset.filter === currentFilter;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
    });
  }

  function addTodo(text) {
    todos.unshift({ id: `${Date.now()}-${Math.random().toString(16).slice(2)}`, text, completed: false });
    saveTodos();
    render();
  }

  function toggleTodo(id) {
    todos = todos.map(todo => todo.id === id ? { ...todo, completed: !todo.completed } : todo);
    saveTodos();
    render();
  }

  function deleteTodo(id) {
    todos = todos.filter(todo => todo.id !== id);
    saveTodos();
    render();
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    addTodo(text);
    form.reset();
    input.focus();
  });

  clearCompleted.addEventListener('click', () => {
    todos = todos.filter(todo => !todo.completed);
    saveTodos();
    render();
  });

  filterButtons.forEach(button => button.addEventListener('click', () => {
    currentFilter = button.dataset.filter;
    render();
  }));

  render();
})();

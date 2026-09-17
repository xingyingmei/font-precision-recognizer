(() => {
  'use strict';

  const STORAGE_KEY = 'font-precision-recognizer.todos.v1';
  const THEME_KEY = 'font-precision-recognizer.theme.v1';
  const form = document.querySelector('#todo-form');
  const input = document.querySelector('#todo-input');
  const priorityInput = document.querySelector('#todo-priority');
  const dueDateInput = document.querySelector('#todo-due-date');
  const list = document.querySelector('#todo-list');
  const emptyState = document.querySelector('#empty-state');
  const count = document.querySelector('#todo-count');
  const clearCompleted = document.querySelector('#clear-completed');
  const themeToggle = document.querySelector('#theme-toggle');
  const filterButtons = [...document.querySelectorAll('[data-filter]')];

  let todos = loadTodos();
  let currentFilter = 'all';
  let draggedId = null;
  let editingId = null;

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

  function loadTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved === 'dark') {
      document.body.classList.add('dark');
      return 'dark';
    }
    document.body.classList.remove('dark');
    return 'light';
  }

  function saveTheme(theme) {
    localStorage.setItem(THEME_KEY, theme);
  }

  function applyTheme(theme) {
    document.body.classList.toggle('dark', theme === 'dark');
    themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    themeToggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }

  function visibleTodos() {
    if (currentFilter === 'active') return todos.filter(todo => !todo.completed);
    if (currentFilter === 'completed') return todos.filter(todo => todo.completed);
    return todos;
  }

  function formatDueDate(value) {
    if (!value) return 'No due date';
    const date = new Date(`${value}T00:00:00`);
    return Number.isNaN(date.getTime()) ? 'No due date' : new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' }).format(date);
  }

  function priorityLabel(priority) {
    return priority ? priority.charAt(0).toUpperCase() + priority.slice(1) : 'Medium';
  }

  function render() {
    const visible = visibleTodos();
    list.replaceChildren();
    emptyState.hidden = visible.length !== 0;

    visible.forEach(todo => {
      const item = document.createElement('li');
      item.className = `todo-item${todo.completed ? ' completed' : ''}`;
      item.dataset.id = todo.id;
      item.draggable = true;
      item.title = 'Drag to reorder';
      item.addEventListener('dragstart', handleDragStart);
      item.addEventListener('dragover', handleDragOver);
      item.addEventListener('dragleave', handleDragLeave);
      item.addEventListener('drop', handleDrop);
      item.addEventListener('dragend', handleDragEnd);

      if (todo.id === editingId) {
        item.innerHTML = `
          <div class="todo-editor">
            <div class="todo-editor-row">
              <input type="text" value="${escapeHtml(todo.text)}" aria-label="Edit task name" data-editor-field="text">
              <select data-editor-field="priority" aria-label="Edit task priority">
                <option value="low" ${todo.priority === 'low' ? 'selected' : ''}>Low</option>
                <option value="medium" ${todo.priority === 'medium' || !todo.priority ? 'selected' : ''}>Medium</option>
                <option value="high" ${todo.priority === 'high' ? 'selected' : ''}>High</option>
              </select>
              <input type="date" value="${todo.dueDate || ''}" data-editor-field="dueDate" aria-label="Edit due date">
            </div>
            <div class="editor-actions">
              <button type="button" class="save-edit" data-action="save-edit">Save</button>
              <button type="button" class="cancel-edit" data-action="cancel-edit">Cancel</button>
            </div>
          </div>
        `;

        const saveButton = item.querySelector('[data-action="save-edit"]');
        const cancelButton = item.querySelector('[data-action="cancel-edit"]');
        const textField = item.querySelector('[data-editor-field="text"]');

        saveButton.addEventListener('click', () => {
          const nextText = textField.value.trim();
          const nextPriority = item.querySelector('[data-editor-field="priority"]').value;
          const nextDueDate = item.querySelector('[data-editor-field="dueDate"]').value;

          if (!nextText) {
            textField.focus();
            return;
          }

          saveTaskEdit(todo.id, nextText, nextPriority, nextDueDate);
        });

        cancelButton.addEventListener('click', () => {
          editingId = null;
          render();
        });

        textField.focus();
        textField.select();
      } else {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = todo.completed;
        checkbox.setAttribute('aria-label', `Mark ${todo.text} as complete`);
        checkbox.addEventListener('change', () => toggleTodo(todo.id));

        const text = document.createElement('span');
        text.className = 'todo-text';
        text.textContent = todo.text;

        const main = document.createElement('div');
        main.className = 'todo-main';
        main.append(text);

        const meta = document.createElement('div');
        meta.className = 'meta-row';

        const priorityBadge = document.createElement('span');
        const priorityName = priorityLabel(todo.priority || 'medium');
        priorityBadge.className = `badge priority-${todo.priority || 'medium'}`;
        priorityBadge.textContent = priorityName;

        const dateBadge = document.createElement('span');
        dateBadge.className = 'date-badge';
        dateBadge.textContent = formatDueDate(todo.dueDate);

        meta.append(priorityBadge, dateBadge);
        main.append(meta);
        label.append(checkbox, main);

        const actions = document.createElement('div');
        actions.className = 'todo-actions';

        const editButton = document.createElement('button');
        editButton.type = 'button';
        editButton.className = 'icon-button';
        editButton.textContent = 'Edit';
        editButton.addEventListener('click', () => {
          editingId = todo.id;
          render();
        });

        const deleteButton = document.createElement('button');
        deleteButton.className = 'delete-task';
        deleteButton.type = 'button';
        deleteButton.textContent = '×';
        deleteButton.title = 'Delete task';
        deleteButton.setAttribute('aria-label', `Delete ${todo.text}`);
        deleteButton.addEventListener('click', () => deleteTodo(todo.id));

        actions.append(editButton, deleteButton);
        item.append(label, actions);
      }

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

  function saveTaskEdit(id, nextText, nextPriority, nextDueDate) {
    todos = todos.map(todo => {
      if (todo.id !== id) return todo;
      return {
        ...todo,
        text: nextText,
        priority: nextPriority || 'medium',
        dueDate: nextDueDate || ''
      };
    });
    editingId = null;
    saveTodos();
    render();
  }

  function handleDragStart(event) {
    draggedId = event.currentTarget.dataset.id;
    event.currentTarget.classList.add('is-dragging');
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', draggedId);
  }

  function handleDragOver(event) {
    event.preventDefault();
    if (event.currentTarget.dataset.id !== draggedId) {
      event.currentTarget.classList.add('drag-over');
    }
    event.dataTransfer.dropEffect = 'move';
  }

  function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag-over');
  }

  function handleDrop(event) {
    event.preventDefault();
    const targetId = event.currentTarget.dataset.id;
    if (!draggedId || draggedId === targetId) return;

    const fromIndex = todos.findIndex(todo => todo.id === draggedId);
    const toIndex = todos.findIndex(todo => todo.id === targetId);
    if (fromIndex === -1 || toIndex === -1) return;

    const [movedTodo] = todos.splice(fromIndex, 1);
    todos.splice(toIndex, 0, movedTodo);
    saveTodos();
    render();
  }

  function handleDragEnd(event) {
    draggedId = null;
    event.currentTarget.classList.remove('is-dragging');
    list.querySelectorAll('.drag-over').forEach(item => item.classList.remove('drag-over'));
  }

  function addTodo(text, priority, dueDate) {
    todos.unshift({
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      text,
      completed: false,
      priority: priority || 'medium',
      dueDate: dueDate || ''
    });
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
    if (editingId === id) editingId = null;
    saveTodos();
    render();
  }

  function escapeHtml(str = '') {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    addTodo(text, priorityInput.value, dueDateInput.value);
    form.reset();
    priorityInput.value = 'medium';
    input.focus();
  });

  clearCompleted.addEventListener('click', () => {
    todos = todos.filter(todo => !todo.completed);
    saveTodos();
    render();
  });

  themeToggle.addEventListener('click', () => {
    const nextTheme = document.body.classList.contains('dark') ? 'light' : 'dark';
    saveTheme(nextTheme);
    applyTheme(nextTheme);
  });

  filterButtons.forEach(button => button.addEventListener('click', () => {
    currentFilter = button.dataset.filter;
    render();
  }));

  const initialTheme = loadTheme();
  applyTheme(initialTheme);
  render();
})();

document.addEventListener('DOMContentLoaded', () => {
    const addButton = document.getElementById('add-btn');
    const todoInput = document.getElementById('todo-input');
    const todoList = document.getElementById('todo-list');

    addButton.addEventListener('click', addTodo);

    function addTodo() {
        const taskText = todoInput.value.trim();
        if (taskText === '') return;

        const listItem = document.createElement('li');
        listItem.textContent = taskText;

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => {
            todoList.removeChild(listItem);
        });

        listItem.appendChild(deleteButton);
        todoList.appendChild(listItem);

        todoInput.value = '';
    }
});
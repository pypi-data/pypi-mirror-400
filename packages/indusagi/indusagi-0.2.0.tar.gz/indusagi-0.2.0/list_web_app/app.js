function addItem() {
    const ul = document.getElementById('myList');
    const input = document.getElementById('itemInput');
    const newItemText = input.value.trim();

    if (newItemText !== '') {
        const li = document.createElement('li');
        li.textContent = newItemText;
        ul.appendChild(li);
        input.value = '';
    } else {
        alert('Please enter an item.');
    }
}
let currentInput = '';
let operator = '';
let firstOperand = null;

function appendNumber(number) {
    currentInput += number;
    updateDisplay(currentInput);
}

function setOperation(op) {
    if (currentInput === '') return;
    if (firstOperand === null) {
        firstOperand = parseFloat(currentInput);
    } else if (operator) {
        firstOperand = operate(firstOperand, parseFloat(currentInput), operator);
        updateDisplay(firstOperand);
    }
    operator = op;
    currentInput = '';
}

function calculate() {
    if (firstOperand === null || currentInput === '' || !operator) return;
    const result = operate(firstOperand, parseFloat(currentInput), operator);
    updateDisplay(result);
    firstOperand = result;
    operator = '';
    currentInput = '';
}

function clearDisplay() {
    currentInput = '';
    operator = '';
    firstOperand = null;
    updateDisplay('');
}

function updateDisplay(value) {
    document.getElementById('display').value = value;
}

function operate(a, b, op) {
    switch (op) {
        case '+': return a + b;
        case '-': return a - b;
        case '*': return a * b;
        case '/': return a / b;
        default: return b;
    }
}
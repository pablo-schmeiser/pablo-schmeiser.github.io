// Handle speed slider
const speedSlider = document.getElementById('speedSlider');
const speedValue = document.getElementById('speedValue');
const pauseButton = document.getElementById('pauseButton');
const resetButton = document.getElementById('resetButton');
const clearButton = document.getElementById('clearButton');


speedSlider.addEventListener('input', (event) => {
    const newSpeed = event.target.value;
    speedValue.textContent = newSpeed;
    updateSpeed(newSpeed);
});

pauseButton.addEventListener('click', () => {
    togglePause();
    pauseButton.textContent = isRunning ? '<i class="fa-solid fa-play"></i>' : '<i class="fa-solid fa-pause"></i>';
});

resetButton.addEventListener('click', () => {
    loadInitialConfig();
    pauseButton.textContent = 'Pause';
});

clearButton.addEventListener('click', () => {
    if (!isRunning) {
        grid = Array(rows).fill().map(() => Array(cols).fill(0));
        drawGrid();
    }
});
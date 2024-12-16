// The number of milliseconds per frame (default: 500)
let speed = 500
let isRunning = false;
let initialConfig = []; // Save initial configuration

function nextGen() {
    // Initialize new grid
    const newGrid = Array(rows).fill().map(() => Array(cols).fill(0));

    // Fill in surviving cells
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const neighbors = getLiveNeighbors(row, col);
            // if cell has 3 neighbors, survive no matter if alive or death (simplified rules 2 and 3)
            // if cell is alive and has 2 neighbors also survive (extra condition of rule 3)
            if (neighbors === 3 || (neighbors === 2 && grid[row][col] === 1)) {
                newGrid[row][col] = 1;
            }

        }
    }

    // update current state and draw new grid 
    grid = newGrid;
    drawGrid();
}

// Start the game loop
let gameInterval;

function startGame() {
    if (initialConfig.length === 0) {
        saveInitialConfig();
    }
    if (gameInterval) clearInterval(gameInterval);
    isRunning = true;
    clearButton.disabled = true;
    gameInterval = setInterval(() => {
        nextGeneration();
    }, speed);
}

// Stop the game loop
function stopGame() {
    if (gameInterval) clearInterval(gameInterval);
    isRunning = false;
    clearButton.disabled = false;
}

// Update speed dynamically
function updateSpeed(newSpeed) {
    speed = parseInt(newSpeed);
    if (gameInterval) {
        startGame();
    }
}

// Toggle the game on and off
function togglePause() {
    if (isRunning) {
        stopGame();
    } else {
        startGame();
    }
}

function saveInitialConfig() {
    initialConfig = grid.map(row => row.slice());
}

// Load the saved initial configuration
function loadInitialConfig() {
    if (initialConfig.length > 0) {
        stopGame();
        grid = initialConfig.map(row => row.slice());
        drawGrid();
    }
}
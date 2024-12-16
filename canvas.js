const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const canvasSize = Math.min(viewportWidth * 0.8, viewportHeight * 0.8);
const cellSize = 20;
const rows = Math.floor(canvasSize / cellSize);
const cols = Math.floor(canvasSize / cellSize);

canvas.width = cols * cellSize;
canvas.height = rows * cellSize;

// Initializes 2D-Array representing the grids cells and initializes them with 0 as their value.
let grid = Array(rows).fill().map(() => Array(cols).fill(0));

// Draws Grid on in the supplied canvas context
function drawGrid() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw cells
    for (let row = 0; row < rows; row++) {canvasSize
        for (let col = 0; col < cols; col++) {
            ctx.fillStyle = grid[row][col] ? 'black' : 'white';
            ctx.fillRect(col * cellSize, row * cellSize, cellSize, cellSize);
            ctx.strokeStyle = 'gray';
            ctx.strokeRect(col * cellSize, row * cellSize, cellSize, cellSize);
        }
    }
}

// Returns cell coordinates for mouse click
function getCellCoordinates(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    return {
        row: Math.floor(y / cellSize),
        col: Math.floor(x / cellSize)
    };
}

// Toggle cell state on click
canvas.addEventListener('click', (event) => {
    const { row, col } = getCellCoordinates(event);
    grid[row][col] = grid[row][col] ? 0 : 1;
    drawGrid();
});

// Initially draw the grid
drawGrid();
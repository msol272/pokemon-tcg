let currentSelectedCell1 = null;
let currentSelectedCell2 = null;

// Card selection and movement logic
document.querySelectorAll('.cell-container').forEach(cell => {
    cell.addEventListener('click', function() {
        // Clear previous selection
        if (seat === 1) {
            if (currentSelectedCell1) {
                currentSelectedCell1.classList.remove('selected-red');
            }

            // Add selected border based on seat
            this.classList.add('selected-red');

            // Store the selected cell
            currentSelectedCell1 = this;
        } else {
            if (currentSelectedCell2) {
                currentSelectedCell2.classList.remove('selected-blue');
            }

            // Add selected border based on seat
            this.classList.add('selected-blue');

            // Store the selected cell
            currentSelectedCell2 = this;
        }

        // Send the selection to the server via WebSocket
        socket.emit('cell_selected', {
            spot: this.getAttribute("for")
        });
    });
});

// Button events
let actionButton = document.getElementById("actionButton");
actionButton.addEventListener('click', function() {
    setActionButton(actionButton.textContent, false)
    socket.emit('action_button', {'action': actionButton.textContent, 'seat': seat});
});

let coinButton = document.getElementById("coinButton");
coinButton.addEventListener('click', function() {
    if (coinButton.textContent === "Flip a Coin") {
        socket.emit('coin_button', username);
    } else {
        setCoinButton(false, "");
    }
});

let newGameButton = document.getElementById("newGameButton");
newGameButton.addEventListener('click', function() {
    let response = confirm("Are you sure?")
    if (response) {
        socket.emit('new_game');
    }
});

// When the document is fully loaded, emit the join_game event
document.addEventListener('DOMContentLoaded', function() {
    // Emit 'join_game' event to the server with the user data
    socket.emit('join_game', { username: username, deckname: deckname, seat: seat });
});


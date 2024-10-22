let currentSelectedCell1 = null;
let currentSelectedCell2 = null;
let moveInProgress = false;
let moveAllInProgress = false;
let moveSrc = '';
let moveIdx = 0;

// Set which cell is selected
function setSelectedCell(cell) {
    if (moveInProgress) {
        let fromPrefix = moveSrc.split('-')[0]
        let toPrefix = cell.getAttribute('for').split('-')[0]

        if (fromPrefix !== toPrefix) {
            alert("Cannot move a card from one seat's area to the other!")
        } else {
            let visible = false;
            if (document.getElementById(moveSrc).hasAttribute('face-up') ||
                document.getElementById(cell.getAttribute('for')).hasAttribute('face-up')) {
                visible = true;
            }
            socket.emit('move_card', {'to_stack': cell.getAttribute('for'), 
                                      'from_stack': moveSrc,
                                      'card_idx': moveIdx,
                                      'visible': visible,
                                      'username': username});        
            moveInProgress = false;
            setMoveButtonSelected(moveIdx, false);
        }
    } else if (moveAllInProgress) {
        let fromPrefix = moveSrc.split('-')[0]
        let toPrefix = cell.getAttribute('for').split('-')[0]

        if (fromPrefix !== toPrefix) {
            alert("Cannot move a card from one seat's area to the other!")
        } else {
            let in_play = false;
            if (document.getElementById(moveSrc).getAttribute('stack-type') === 'in-play' &&
                document.getElementById(cell.getAttribute('for')).getAttribute('stack-type') === 'in-play') {
                in_play = true;
            }
            socket.emit('move_stack', {'to_stack': cell.getAttribute('for'), 
                                       'from_stack': moveSrc,
                                       'in_play': in_play,
                                       'username': username});
            moveAllInProgress = false;
            setMoveAllButtonSelected(false);
        }
    } else {
        // Clear previous selection
        if (seat === 1) {
            if (currentSelectedCell1) {
                currentSelectedCell1.classList.remove('selected-red');
            }

            // Add selected border based on seat
            cell.classList.add('selected-red');

            // Store the selected cell
            currentSelectedCell1 = cell;
        } else {
            if (currentSelectedCell2) {
                currentSelectedCell2.classList.remove('selected-blue');
            }

            // Add selected border based on seat
            cell.classList.add('selected-blue');

            // Store the selected cell
            currentSelectedCell2 = cell;
        }

        // Send the selection to the server via WebSocket
        socket.emit('cell_selected', {
            spot: cell.getAttribute("for")
        });
    }
}

// Card selection and movement logic
document.querySelectorAll('.cell-container').forEach(cell => {
    cell.addEventListener('click', function() {
        setSelectedCell(this);
    });
});

// Button events
function handleDrawButtonClick(event) {
    const clickedButton = event.target;
    const src = clickedButton.getAttribute('for');
    let dst = 'seat1-hand';
    if (seat === 2) {
        dst = 'seat2-hand';
    }
    socket.emit('move_card', {'from_stack': src, 'to_stack': dst, 'card_idx': 0, 'visible':false, 'username':username});
    let srcText = document.querySelector(`label[for="${src}"]`).innerText;
}

function handleShuffleButtonClick(event) {
    const clickedButton = event.target;
    const stack = clickedButton.getAttribute('for');
    socket.emit('shuffle_stack', stack);
    let stackText = document.querySelector(`label[for="${stack}"]`).innerText;
    socket.emit('log_event', `${username} shuffled ${stackText}`);
}

function handleMoveButtonClick(event, idx) {
    const clickedButton = event.target;
    let stack = ""
    if (seat === 1) {
        stack =  currentSelectedCell1.getAttribute('for')
    } else {
        stack =  currentSelectedCell2.getAttribute('for')
    }
    // If this button was already selected, just undo it.
    if (moveInProgress && moveIdx === idx) {
        moveInProgress = false;
        setMoveButtonSelected(moveIdx, false);
    } else {
        // Unselect any other buttons that are pressed
        if (moveAllInProgress) {
            setMoveAllButtonSelected(false);
        }
        if (moveInProgress) {
            setMoveButtonSelected(moveIdx, false);
        }
        setMoveButtonSelected(idx, true);
        moveInProgress = true;
        moveAllInProgress = false;
        moveSrc = stack;
        moveIdx = idx;
    }
}

function handleIncrementDamageClick(event) {
    const clickedButton = event.target;
    const stack = clickedButton.getAttribute('for')
    socket.emit('add_damage', {'stack': stack, 'username': username})
}
function handleDecrementDamageClick(event) {
    const clickedButton = event.target;
    const stack = clickedButton.getAttribute('for')
    socket.emit('remove_damage', {'stack': stack, 'username': username})    
}
function handleConditionButtonClick(event) {
    const clickedButton = event.target;
    const spot = clickedButton.getAttribute('for')   
    socket.emit('toggle_condition', {'spot': spot, 'username': username})
}

function handleFlipButtonClick(event, idx) {
    const clickedButton = event.target;
    const card_idx = clickedButton.getAttribute('card-idx');
    const card_id = clickedButton.getAttribute('card-id');
    flipCard(card_idx, card_id, true);
}

function handleMoveAllButtonClick(event) {
    const clickedButton = event.target;
    let stack = ""
    if (seat === 1) {
        stack =  currentSelectedCell1.getAttribute('for')
    } else {
        stack =  currentSelectedCell2.getAttribute('for')
    }
    if (moveAllInProgress) {
        moveAllInProgress = false;
        setMoveAllButtonSelected(false);
    } else {
        if (moveInProgress) {
            moveInProgress = false;
            setMoveButtonSelected(moveIdx, false);
        }
        setMoveAllButtonSelected(true);
        moveAllInProgress = true;
        moveSrc = stack;
    }
}

function handleFlipAllButtonClick(event) {
    // Find all flip buttons
    const buttons = document.querySelectorAll('button');
    const flipButtons = Array.from(buttons).filter(button => button.innerText === 'Flip');

    for (const button of flipButtons) {
        const card_idx = button.getAttribute('card-idx');
        const card_id = button.getAttribute('card-id');
        flipCard(card_idx, card_id, false);
    }
}

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

let moveAllButton = document.getElementById("move-all-btn");
moveAllButton.addEventListener('click', function(event) {
    handleMoveAllButtonClick(event);
});

let flipAllButton = document.getElementById("flip-all-btn");
flipAllButton.addEventListener('click', function(event) {
    handleFlipAllButtonClick(event);
});

// When the document is fully loaded, emit the join_game event
document.addEventListener('DOMContentLoaded', function() {
    // Emit 'join_game' event to the server with the user data
    socket.emit('join_game', { username: username, deckname: deckname, seat: seat });
});


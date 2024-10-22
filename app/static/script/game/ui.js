if (seat === 1) {
    // Make seat 2's drawable stacks not drawable for this user
    document.getElementById("seat2-deck").setAttribute("stack-type", "default");
    document.getElementById("seat2-prizes").setAttribute("stack-type", "default");
} else {
    // Make seat 1's drawable stacks not drawable for this user
    document.getElementById("seat1-deck").setAttribute("stack-type", "default");
    document.getElementById("seat1-prizes").setAttribute("stack-type", "default");
    // Flip layout for seat 2
    gameboard.classList.add('flip-layout');
}

/*******************************************************************************
 * Helper functions
 ******************************************************************************/

/* Callback for clicking on a card */
function openModal(img) {
    const modal = document.getElementById("modal");
    const modalImage = document.getElementById("modal-image");

    // Set the image source and caption
    modalImage.src = img.src;

    // Display the modal
    modal.style.display = "block";
}

/* Callback for closing modal */
function closeModal() {
    const modal = document.getElementById("modal");
    modal.style.display = "none"; // Hide the modal
}

function setStatusText(text, your_turn) {
    const statusText = document.getElementById("statusText");
    statusText.textContent = text;
    if (your_turn) {
        statusText.classList.add('status-your-turn'); 
    } else {
        statusText.classList.remove('status-your-turn');         
    }
}

function setCardsVisible(visible) {
    if (visible) {
        document.getElementById('seat1-b1').setAttribute('face-up', '');
        document.getElementById('seat1-b2').setAttribute('face-up', '');
        document.getElementById('seat1-b3').setAttribute('face-up', '');
        document.getElementById('seat1-b4').setAttribute('face-up', '');
        document.getElementById('seat1-b5').setAttribute('face-up', '');
        document.getElementById('seat1-active').setAttribute('face-up', '');
        document.getElementById('seat2-b1').setAttribute('face-up', '');
        document.getElementById('seat2-b2').setAttribute('face-up', '');
        document.getElementById('seat2-b3').setAttribute('face-up', '');
        document.getElementById('seat2-b4').setAttribute('face-up', '');
        document.getElementById('seat2-b5').setAttribute('face-up', '');
        document.getElementById('seat2-active').setAttribute('face-up', '');
    } else {
        document.getElementById('seat1-b1').removeAttribute('face-up');
        document.getElementById('seat1-b2').removeAttribute('face-up');
        document.getElementById('seat1-b3').removeAttribute('face-up');
        document.getElementById('seat1-b4').removeAttribute('face-up');
        document.getElementById('seat1-b5').removeAttribute('face-up');
        document.getElementById('seat1-active').removeAttribute('face-up');
        document.getElementById('seat2-b1').removeAttribute('face-up');
        document.getElementById('seat2-b2').removeAttribute('face-up');
        document.getElementById('seat2-b3').removeAttribute('face-up');
        document.getElementById('seat2-b4').removeAttribute('face-up');
        document.getElementById('seat2-b5').removeAttribute('face-up');
        document.getElementById('seat2-active').removeAttribute('face-up');     
    }
}

/* Create a view of a card in the view panel */
function createCardView(card, idx, face_up) {
    const cardDiv = document.createElement('div');
    cardDiv.classList.add('card');

    const img = document.createElement('img');
    if (face_up) {
        img.src = `/static/images/${card.id}.jpg`;
    } else {
        img.src = `/static/images/back.jpg`;
    }
    img.setAttribute('card-idx', idx);
    if (face_up) {
        img.setAttribute('face-up', '');
    }
    img.onclick = function() { 
        openModal(img);
    }
    cardDiv.appendChild(img);

    const buttonsDiv = document.createElement('div');
    buttonsDiv.classList.add('card-buttons');

    const moveBtn = document.createElement('button');
    moveBtn.innerText = 'Move';
    moveBtn.setAttribute('card-idx', idx);
    moveBtn.addEventListener('click', (event) => handleMoveButtonClick(event, idx));
    buttonsDiv.appendChild(moveBtn);

    const flipBtn = document.createElement('button');
    flipBtn.innerText = 'Flip';
    flipBtn.setAttribute('card-idx', idx);
    flipBtn.setAttribute('card-id', card.id);
    flipBtn.addEventListener('click', (event) => handleFlipButtonClick(event, idx));
    buttonsDiv.appendChild(flipBtn);

    cardDiv.appendChild(buttonsDiv);
    return cardDiv;
}


/*******************************************************************************
 * Public functions
 ******************************************************************************/
function setActionButton(text, enable) {
    const actionButton = document.getElementById("actionButton");
    actionButton.textContent = text;
    if (enable) {
        actionButton.classList.remove('disabled-action-button');
        actionButton.classList.add('enabled-action-button');
        actionButton.disabled = false;
    } else {
        actionButton.classList.remove('enabled-action-button');
        actionButton.classList.add('disabled-action-button');
        actionButton.disabled = true;        
    }
}

function setCoinButton(flip_complete, flip_result) {
    const coinButton = document.getElementById("coinButton");
    if (!flip_complete) {
        coinButton.textContent = "Flip a Coin";
        coinButton.classList.remove('coin-flip-result');
        coinButton.classList.add('coin-flip-base');
    } else {
        coinButton.textContent = flip_result;
        coinButton.classList.add('coin-flip-result');
        coinButton.classList.remove('coin-flip-base');        
    }
}

function addHistoryMessage(message) {
    const log = document.createElement('div');
    let historyBox = document.getElementById("historyBox");
    log.textContent = message;
    historyBox.appendChild(log);
    historyBox.scrollTop = historyBox.scrollHeight; // Auto-scroll to bottom
}

function setNewGameButton(enable) {
    let newGameButton = document.getElementById("newGameButton");
    if (enable) {
        newGameButton.classList.remove('disabled-new-game-button');
        newGameButton.classList.add('enabled-new-game-button');
        newGameButton.disabled = false;
    } else {
        newGameButton.classList.remove('enabled-new-game-button');
        newGameButton.classList.add('disabled-new-game-button');
        newGameButton.disabled = true;            
    }
}

function updateGameState(state) {
    if (state === 'ready') {
        setStatusText("Start a Game!", false);
        setActionButton("-", false);
    } else if (state === 'setup') {
        setStatusText("Setup", false);
        setActionButton("Ready", true);
        setCardsVisible(false);
        addHistoryMessage('---New Game---')
    } else if ((state === 'p1-turn' && seat === 1) || 
                   (state === 'p2-turn' && seat === 2)) {
        setStatusText("Your Turn", true);
        setActionButton("End Turn", true);
        setCardsVisible(true);
    } else if ((state === 'p1-turn' && seat === 2) || 
               (state === 'p2-turn' && seat === 1)) {
        setStatusText("Opp Turn", false);
        setActionButton("-", false);
        setCardsVisible(true);
    }
}

function setSeatLabel(seat, user, deck) {
    let label = document.getElementById('seat1-label');
    if (seat == 2) {
        label = document.getElementById('seat2-label');
    }
    label.textContent = user ? `Seat ${seat}: ${user} - ${deck}` : 'Seat 2: (empty)';
}

/* Set the card list for a given cell */
function setCellCards (element_id, cards) {
    const element = document.getElementById(element_id);

    // Preserve custom properties
    const stackType = element.getAttribute("stack-type");
    const faceUp = element.hasAttribute("face-up");

    if (cards.length === 0) {
        // Change to empty-cell
        element.className = "empty-cell";
        element.innerHTML = "";            
    } else {
        let cardImg = "/static/images/back.jpg"
        if (faceUp) {
            cardImg = `/static/images/${cards[0].id}.jpg`
        }

        let controlBar = ``
        if (stackType === "drawable") {
            controlBar = `<div class="controls-row">
                <button class="control-button control-button-normal" for=${element_id}>Draw</button>
                <button class="control-button control-button-normal" for=${element_id}>Shuffle</button>
            </div>`
        } else if (stackType === "in-play") {
            controlBar = `<div class="controls-row">
                <button class="damage-button" for=${element_id}>-</button>
                <input type="text" value="${cards[0].damage}" readonly class="number-input" for=${element_id}>
                <button class="damage-button" for=${element_id}>+</button>
                <button class="control-button ${cards[0].condition === 'NML' ? 'control-button-normal' : 'control-button-special-condition'}" for=${element_id}>${cards[0].condition}</button>
            </div>`
        }

        element.className = "card-cell";
        element.innerHTML = `
            <div class="image-container">
                <img src=${cardImg} alt="Card Image" class="grid-image">
                <div class="overlay">${cards.length}</div>
            </div>
            ${controlBar}`;
    }

    // Restore custom properties after changing the content
    element.setAttribute("stack-type", stackType);
    if (faceUp) {
        element.setAttribute("face-up", "");
    }

    // Add action listeners to buttons
    document.querySelectorAll(`.control-button[for="${element_id}"]`).forEach(button => {
      buttonText = button.textContent.trim()
      if (buttonText === 'Draw') {
        button.addEventListener('click', handleDrawButtonClick);
      } else if (buttonText === 'Shuffle') {
        button.addEventListener('click', handleShuffleButtonClick);        
      } else  {
        button.addEventListener('click', handleConditionButtonClick);        
      }
    });

    document.querySelectorAll(`.damage-button[for="${element_id}"]`).forEach(button => {
      buttonText = button.textContent.trim()
      if (buttonText === '+') {
        button.addEventListener('click', handleIncrementDamageClick);
      } else  {
        button.addEventListener('click', handleDecrementDamageClick);        
      }

    });

}

function setDamage(spot, damage) {
    dmgField = document.querySelectorAll(`.number-input[for="${spot}"]`)[0]
    dmgField.value = damage;
}

function setCondition(spot, condition) {
    const element = document.querySelectorAll(`.control-button[for=${spot}]`)[0]
    element.innerText = condition;
    if (condition === "NML") {
        element.classList.remove('control-button-special-condition');
        element.classList.add('control-button-normal');
    } else {
        element.classList.remove('control-button-normal');
        element.classList.add('control-button-special-condition');
    }
}

/* Set the view panel's card list */
function setViewPanelCards(cards, spot) {
  let face_up = document.getElementById(spot).hasAttribute('face-up');
  if (spot === `seat${seat}-hand`) {
    face_up = true;
  }
  const cardPanel = document.getElementById('card-panel');
  cardPanel.innerHTML = ''; // Clear existing content
  let idx = 0
  cards.forEach(card => {
    const cardElement = createCardView(card, idx, face_up);
    cardPanel.appendChild(cardElement,);
    idx = idx + 1;
  });
}

function setMoveAllButtonSelected(selected) {
    const btn = document.getElementById('move-all-btn')
    if (selected) {
        btn.classList.add('selected-move');
    } else {
        btn.classList.remove('selected-move');
    }
}

function setMoveButtonSelected(idx, selected) {
    const btn = document.querySelectorAll(`button[card-idx="${idx}"]`)[0]
    if (selected) {
        btn.classList.add('selected-move');
    } else {
        btn.classList.remove('selected-move');
    }
}

function flipCard(idx, card_id, single_card) {
    const img = document.querySelector(`img[card-idx="${idx}"]`);
    if (img.hasAttribute('face-up')) {
        img.removeAttribute('face-up');
        img.src = `/static/images/back.jpg`;
    } else {
        img.setAttribute('face-up', '');
        img.src = `/static/images/${card_id}.jpg`;
        // Check if this user is peaking at a hidden card
        let stack = ''
        if (seat === 1) {
            stack = currentSelectedCell1.getAttribute('for')
            hand = 'seat1-hand'
        } else {
            stack = currentSelectedCell2.getAttribute('for')
            hand = 'seat2-hand'
        }
        let visible = stack === hand || document.getElementById(stack).hasAttribute('face-up')
        if (!visible) {
            let stackText = document.querySelector(`label[for="${stack}"]`).innerText;
            if (single_card) {
                socket.emit('log_event', `${username} peeked at card ${idx} in ${stackText}`)
            } else if (idx === "0") {
                socket.emit('log_event', `${username} peeked at all cards in ${stackText}`)
            }
        }
    }
}

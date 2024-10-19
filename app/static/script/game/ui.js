// Flip layout for seat 2
if (seat === 2) {
    gameboard.classList.add('flip-layout');
}

/*******************************************************************************
 * Helper functions
 ******************************************************************************/
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
function createCardView(card) {
    const cardDiv = document.createElement('div');
    cardDiv.classList.add('card');

    const img = document.createElement('img');
    img.src = `/static/images/${card.id}.jpg`;
    cardDiv.appendChild(img);

    const buttonsDiv = document.createElement('div');
    buttonsDiv.classList.add('card-buttons');

    const moveBtn = document.createElement('button');
    moveBtn.innerText = 'Move';
    moveBtn.addEventListener('click', () => moveCard(card.id));
    buttonsDiv.appendChild(moveBtn);

    const flipBtn = document.createElement('button');
    flipBtn.innerText = 'Flip';
    flipBtn.addEventListener('click', () => flipCard(card.id));
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
                <button class="control-button">Draw</button>
                <button class="control-button">Shuffle</button>
            </div>`
        } else if (stackType === "in-play") {
            controlBar = `<div class="controls-row">
                <button class="damage-button">-</button>
                <input type="text" value="1" class="number-input">
                <button class="damage-button">+</button>
                <button class="control-button">NML</button>
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
}setSeatLabel

/* Set the view panel's card list */
function setViewPanelCards(cards) {
  const cardPanel = document.getElementById('card-panel');
  cardPanel.innerHTML = ''; // Clear existing content
  cards.forEach(card => {
    const cardElement = createCardView(card);
    cardPanel.appendChild(cardElement);
  });
}

// Initialize highlight for cards that already have a count > 0
document.querySelectorAll('span[id^="count-"]').forEach(function(span) {
    const cardNumber = span.id.replace('count-', ''); // Get the card ID from the span's ID
    const card = document.getElementById(`card-${cardNumber}`);
    const count = parseInt(span.innerText);

    if (count > 0) {
        card.classList.add('highlight');
    }
});


/*******************************************************************************
 * Helper functions
 ******************************************************************************/
/* Update the summary statistics after a card is added or removed */
function updateSummary() {
    let totalPokemonCount = 0;
    let uniquePokemonCount = 0;
    let totalEnergyCount = 0;
    let uniqueEnergyCount = 0;
    let totalTrainerCount = 0;
    let uniqueTrainerCount = 0;

    // Get all cards and their counts
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        const cardType = card.getAttribute('card-type');
        const cardId = card.getAttribute('card-id');
        let countElement = document.getElementById(`count-${cardId}`);
        const count = parseInt(countElement.innerText) || 0;

        if (count > 0) {
            if (cardType === 'Energy') {
                totalEnergyCount += count;
                uniqueEnergyCount += 1
            } else if (cardType === 'Trainer') {
                totalTrainerCount += count;
                uniqueTrainerCount += 1
            } else {
                totalPokemonCount += count;
                uniquePokemonCount += 1
            }
        }
    });

    // Update the summary panel
    const summaryPanel = document.querySelector('.summary-panel');
    summaryPanel.querySelector('ul li:nth-child(1)').innerText = `Pokémon: ${totalPokemonCount} (${uniquePokemonCount} unique)`;
    summaryPanel.querySelector('ul li:nth-child(2)').innerText = `Trainers: ${totalTrainerCount} (${uniqueTrainerCount} unique)`;
    summaryPanel.querySelector('ul li:nth-child(3)').innerText = `Energy: ${totalEnergyCount} (${uniqueEnergyCount} unique)`;
    summaryPanel.querySelector('ul li:last-child strong').innerText = `Total: ${totalPokemonCount + totalTrainerCount + totalEnergyCount} (${uniquePokemonCount + uniqueTrainerCount + uniqueEnergyCount} unique)`;
}

/* Update hidden input associated with a card */ 
function updateHiddenInput(cardId) {
    const countSpan = document.getElementById(`count-${cardId}`);
    const hiddenInput = document.getElementById(`hidden-count-${cardId}`);
    const count = countSpan.innerText; // Extract the current count
    hiddenInput.value = count; // Update hidden input value
}

/*******************************************************************************
 * Callbacks
 ******************************************************************************/

/* Callback for + button on a card */
function increaseCount(cardNumber) {
    const card = document.getElementById(`card-${cardNumber}`);

    let countElement = document.getElementById(`count-${cardNumber}`);
    let totalElement = document.getElementById(`total-${cardNumber}`);
    
    let currentCount = parseInt(countElement.innerText);
    let totalCount = parseInt(totalElement.innerText);

    // Only increase if current count is less than total available
    if (currentCount < totalCount) {
        countElement.innerText = currentCount + 1;
        updateHiddenInput(cardNumber); // Sync with hidden input
    }
    if (currentCount + 1 > 0) {
        card.classList.add('highlight');
    }
    updateSummary();
}

/* Callback for - button on a card */
function decreaseCount(cardNumber) {
    const card = document.getElementById(`card-${cardNumber}`);

    let countElement = document.getElementById(`count-${cardNumber}`);
    
    let currentCount = parseInt(countElement.innerText);
    
    // Only decrease if current count is greater than zero
    if (currentCount > 0) {
        countElement.innerText = currentCount - 1;
        updateHiddenInput(cardNumber); // Sync with hidden input
    }
    if (currentCount - 1 <= 0) {
        card.classList.remove('highlight');
    }
    updateSummary();
}

/* Callback for filtering controls */
function filterCards() {
    const query = document.getElementById('search-bar').value.toLowerCase();
    const viewMode = document.getElementById('view-mode').value;
    const type = document.getElementById('card-type').value;
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        const cardName = card.querySelector('img').alt.toLowerCase();
        const cardId = card.getAttribute('card-id');
        let countElement = document.getElementById(`count-${cardId}`);
        let totalElement = document.getElementById(`total-${cardId}`);
        const count = parseInt(countElement.innerText) || 0;
        const total = parseInt(totalElement.innerText) || 0;
        const cardType = card.getAttribute('card-type');

        // Check if card matches the search query
        const matchesQuery = cardName.includes(query);

        // Check if card matches the view mode (all, indeck, notindeck)
        let matchesViewMode = true;
        if (viewMode === 'indeck' && count === 0) {
            matchesViewMode = false;
        } else if (viewMode === 'available' && count >= total) {
            matchesViewMode = false;
        }

        // Check if card matches the energy type (or 'all' if no filter)
        let matchesType = false;
        if (type === 'All') {
            matchesType = true;
        } else if (type === cardType) {
            matchesType = true;
        }

        // Show or hide card based on all filters
        if (matchesQuery && matchesViewMode && matchesType) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/* Callback for Save button */
function validateDeck() {
    let totalCards = 0;

    // Loop through all hidden inputs (which contain the counts)
    document.querySelectorAll('input[type="hidden"]').forEach(function(input) {
        totalCards += parseInt(input.value); // Add up the card counts
    });

    // Check if the total number of cards is exactly 60
    if (totalCards !== 60) {
        const errorMessage = document.getElementById('error-message');
        if (totalCards < 60) {
            errorMessage.textContent = `Too few cards! Your deck has ${totalCards} cards. You need 60.`;
        } else {
            errorMessage.textContent = `Too many cards! Your deck has ${totalCards} cards. You need 60.`;
        }
        errorMessage.style.display = 'block'; // Show error message
        return false; // Prevent form submission
    }

    return true; // Allow form submission if deck is exactly 60 cards
}

/* Callback for clicking on a card */
function openModal(cardNumber) {
    const modal = document.getElementById("modal");
    const modalImage = document.getElementById("modal-image");
    const caption = document.getElementById("caption");

    // Set the image source and caption
    modalImage.src = document.getElementById(`img-${cardNumber}`).src; // Get the clicked card's image source
    caption.innerHTML = document.getElementById(`img-${cardNumber}`).alt; // Get the card's name for caption

    // Display the modal
    modal.style.display = "block";
}

/* Callback for closing modal */
function closeModal() {
    const modal = document.getElementById("modal");
    modal.style.display = "none"; // Hide the modal
}

// Initialize highlight for cards that already have a count > 0
document.querySelectorAll('input[type="text"]').forEach(function(input) {
    const cardNumber = input.name;
    const card = document.getElementById(`card-${cardNumber}`);
    if (parseInt(input.value) > 0) {
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
        const input = card.querySelector('input[type="text"]');
        const count = parseInt(input.value) || 0;

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

/*******************************************************************************
 * Callbacks
 ******************************************************************************/

/* Callback for + button on a card */
function increaseCount(cardNumber) {
    const input = document.getElementById(`count-${cardNumber}`);
    const card = document.getElementById(`card-${cardNumber}`);
    let currentValue = parseInt(input.value) || 0;
    input.value = currentValue + 1;

    if (currentValue + 1 > 0) {
        card.classList.add('highlight');
    }
    updateSummary();
}

/* Callback for - button on a card */
function decreaseCount(cardNumber) {
    const input = document.getElementById(`count-${cardNumber}`);
    const card = document.getElementById(`card-${cardNumber}`);
    let currentValue = parseInt(input.value) || 0;

    if (currentValue > 0) {
        input.value = currentValue - 1;
    }

    if (currentValue - 1 <= 0) {
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
        const count = parseInt(card.querySelector('input[type="text"]').value) || 0;
        const cardType = card.getAttribute('card-type');

        // Check if card matches the search query
        const matchesQuery = cardName.includes(query);

        // Check if card matches the view mode (all, owned, unowned)
        let matchesViewMode = true;
        if (viewMode === 'owned' && count === 0) {
            matchesViewMode = false;
        } else if (viewMode === 'unowned' && count > 0) {
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

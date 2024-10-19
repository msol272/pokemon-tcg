// Open the Rename Modal
function openRenameModal(deckName) {
    document.getElementById('current-deck-name').value = deckName;
    document.getElementById('rename-modal').style.display = 'block';
}

// Open the Delete Modal
function openDeleteModal(deckName) {
    document.getElementById('deck-to-delete').value = deckName;
    document.getElementById('delete-modal').style.display = 'block';
}

// Close any modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modals when clicking outside of them
window.onclick = function(event) {
    const renameModal = document.getElementById('rename-modal');
    const deleteModal = document.getElementById('delete-modal');
    if (event.target === renameModal) {
        closeModal('rename-modal');
    }
    if (event.target === deleteModal) {
        closeModal('delete-modal');
    }
}

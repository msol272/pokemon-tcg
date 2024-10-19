var socket = io();

// Update to the participant list
socket.on('player_update', function(data) {
    setSeatLabel(1, data.user1, data.deck1);
    setSeatLabel(2, data.user2, data.deck2);
});

// Add action to the history log
socket.on('action_log', function(message) {
    addHistoryMessage(message);
});

// Error popup
socket.on('error', function(data) {
    alert(data.message)
});

// Sync the status of the board
socket.on('sync_board', function(data) {
    for (const key in data) {
        setCellCards(key, data[key]);
    }
});

// Set the cards for a given cell
socket.on('set_cell_cards', function(data) {
    setCellCards(data.spot, data.cards);
});

socket.on('set_view_panel_cards', function(data) {
    setViewPanelCards(data)
});


socket.on('set_new_game_enable', function(enable) {
    setNewGameButton(enable)
});

// Change game state text and button
socket.on('game_state_change', function(state) {
    updateGameState(state);
});

socket.on('coin_flip_result', function(data) {
    addHistoryMessage(`${data.user} coin: ${data.result}`);
    setCoinButton(true, data.result)
});

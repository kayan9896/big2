import React, { useState } from 'react';

const App = () => {
  const link='https://studious-fiesta-qg6rjrrwp4rhxq4p-5000.app.github.dev/'
  const [gameState, setGameState] = useState('start'); // Possible states: 'start', 'waiting', 'gameStarted'
  const [gameData, setGameData] = useState(null);

  const startGame = async () => {
    setGameState('waiting');
    try {
      const response = await fetch(link+'start'); // Replace '/start-game' with your actual backend endpoint
      const data = await response.json();
      setGameData(data);
      setGameState('gameStarted');
    } catch (error) {
      console.error('Error starting game:', error);
      setGameState('start');
    }
  };

  const renderCardArea = (playerId, cards) => {
    if (!cards || cards.length === 0) {
      return <div>No cards</div>;
    }

    if (playerId === gameData.player_id) {
      return (
        <div>
          {cards.map((card, index) => (
            <img key={index} src={card.image} alt={`Card ${index}`} />
          ))}
        </div>
      );
    } else {
      return <div>{cards.length} card(s) uncovered</div>;
    }
  };

  return (
    <div>
      {gameState === 'start' && <button onClick={startGame}>Start Game</button>}
      {gameState === 'waiting' && <div>Waiting for game to start...</div>}
      {gameState === 'gameStarted' && (
        <div>
          <div>Top: {renderCardArea(1, gameData.cards[1])}</div>
          <div>
            Left: {renderCardArea(2, gameData.cards[2])}
            &nbsp;&nbsp;&nbsp;&nbsp;
            Right: {renderCardArea(3, gameData.cards[3])}
          </div>
          <div>Bottom (Your cards): {renderCardArea(gameData.player_id, gameData.cards[gameData.player_id])}</div>
        </div>
      )}
    </div>
  );
};

export default App;

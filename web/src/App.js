
  import React, { useState, useEffect } from 'react';
  import './App.css'; // Assuming a CSS file for styling
  
  function App() {
    const link='https://studious-fiesta-qg6rjrrwp4rhxq4p-5000.app.github.dev/'
    const [ gameState, setGameState ] = useState('notStarted'); // 'notStarted', 'waiting', 'inProgress'
    const [ gameData, setGameData ] = useState(null);
    const suit={1:'spades',2:'hearts',3:'clubs',4:'diamonds'}
    const startGame = async () => {
      setGameState('waiting');
      const response = await fetch(link+'start'); // Replace 'link' with your backend endpoint
      const data = await response.json();
      if (data.game_id) {
        setGameData(data);
        setGameState('inProgress');
      } else {
        setGameState('notStarted');
      }
    };
  
    const renderCardArea = (playerIndex) => {
      const numCards = gameData.player_id === playerIndex ? gameData.cards[playerIndex].length : 2; // Assuming 2 cards per player for simplicity
      
      return (
        <div className={`card-area ${gameData.player_id === playerIndex ? 'player-area' : ''}`}>
          {Array.from({ length: numCards }, (_, i) => (
            <div>
            <img key={i} src={gameData.player_id === playerIndex ? require(`./cards/card_${suit[gameData.cards[playerIndex][i][1]]}_${gameData.cards[playerIndex][i][0]===13?13:gameData.cards[playerIndex][i][0]%13}.png`) : require('./cards/card_back.png')} alt="card" /> 
            </div>))}
        </div>
      );
    };
  
    return (
      <div className="App">
        {gameState === 'notStarted' && <button onClick={startGame}>Start Game</button>}
        {gameState === 'waiting' && <div>Waiting for game...</div>}
        {gameState === 'inProgress' && (
          <div className='table'>
            {renderCardArea((gameData.player_id + 3) % 4)}
            <div style={{justifyContent:'space-between',display:'flex',flexDirection:'row'}}>
            {renderCardArea((gameData.player_id + 2) % 4)}
            {renderCardArea((gameData.player_id + 1) % 4)} 
            </div>
            {renderCardArea(gameData.player_id)} // Bottom: Player
          </div>
        )}
      </div>
    );
  }
  
  export default App;
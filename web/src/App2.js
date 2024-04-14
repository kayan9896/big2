
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
  
    const renderCardArea = (playerIndex,area) => {
      
      return (
        <div className={`card-area ${gameData.player_id === playerIndex ? 'player-area' : ''} ${area}`}>
          <p>Player {playerIndex}</p>
          {gameData.cards[playerIndex].map((card, i) => (
          <div key={i}>
            <img src={gameData.player_id === playerIndex ? require(`./cards/card_${suit[card[1]]}_${card[0] === 13 ? 13 : card[0] % 13}.png`)
                  : require('./cards/card_back.png')}alt="card"/>
          </div>))
          }
        </div>
      );
    };
  
    return (
      <div className="App">
        {gameState === 'notStarted' && <button onClick={startGame}>Start Game</button>}
        {gameState === 'waiting' && <div>Waiting for game...</div>}
        {gameState === 'inProgress' && (
          <div className='table'>
            {renderCardArea((gameData.player_id + 2) % 4,'top')}
            <div style={{justifyContent:'space-between',display:'flex',flexDirection:'row'}}>
            {renderCardArea((gameData.player_id + 3) % 4,'right')}
            {renderCardArea((gameData.player_id + 1) % 4,'left')} 
            </div>
            {renderCardArea(gameData.player_id,'')} // Bottom: Player
          </div>
        )}
      </div>
    );
  }
  
  export default App;
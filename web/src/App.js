
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
    const [selectedCards, setSelectedCards] = useState([]);

    const handleCardClick = (index) => {
      setSelectedCards((prevSelected) => {
        if (prevSelected.includes(index)) {
          return prevSelected.filter((i) => i !== index); // Deselect
        } else {
          return [...prevSelected, index]; // Select
        }
      });
    };
    const renderCardArea = (playerIndex) => {

      const rotationClass = playerIndex === (gameData.player_id + 3) % 4 ? 'rotate90'
                         : playerIndex === (gameData.player_id + 1) % 4 ? 'rotate270'
                         : ''; 
                         
      return (
        <div className={`card-area ${rotationClass} ${gameData.player_id === playerIndex ? 'player-area' : ''}`}>
          <p>Player {playerIndex}</p>
          {gameData.cards[playerIndex].map((card, i) => (
          <div key={i}>
            <img src={gameData.player_id === playerIndex ? require(`./cards/card_${suit[card[1]]}_${card[0] === 13 ? 13 : card[0] % 13}.png`)
                  : require('./cards/card_back.png')} alt="card" 
                  className={(selectedCards.includes(i)) ? 'selected' : ''}
                  onClick={() => handleCardClick(i)}/>
          </div>))
          }
        </div>
      );
    };

    function lastCard(){
      return (
        <div className={'last'}>
          {gameData.cards[0].map((card, i) => (
          <div key={i}>
            {i<5?<img src={require(`./cards/card_${suit[card[1]]}_${card[0] === 13 ? 13 : card[0] % 13}.png`)} alt="card" />:null}
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
            {renderCardArea((gameData.player_id + 3) % 4)}
            <div className='table2'>
            {renderCardArea((gameData.player_id + 2) % 4)}
            {lastCard()}
            {renderCardArea(gameData.player_id)}
            </div>
            {renderCardArea((gameData.player_id + 1) % 4)} 
          </div>
            
        )}
      </div>
    );
  }
  
  export default App;
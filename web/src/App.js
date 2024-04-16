
  import React, { useState, useEffect } from 'react';
  import './App.css'; // Assuming a CSS file for styling
  
  function App() {
    const link='https://studious-fiesta-qg6rjrrwp4rhxq4p-5000.app.github.dev/'
    const [ gameState, setGameState ] = useState('notStarted'); // 'notStarted', 'waiting', 'inProgress'
    const [ gameData, setGameData ] = useState(null);
    const [turn,setTurn]=useState(null)
    const [last,setLast]=useState(null)
    const [handcards,setHandcards]=useState(null)
    const suit={1:'spades',2:'hearts',3:'clubs',4:'diamonds'}
    const startGame = async () => {
      setGameState('waiting');
      try{
      const response = await fetch(link+'start'); // Replace 'link' with your backend endpoint
      const data = await response.json();
      if (data.game_id) {
        setGameData(data);
        setGameState('inProgress');
        setHandcards(data.cards)
        setTurn(data.turn)
      }} catch(e) {
        setGameState('notStarted');
        console.log(e)
      }
    };
    const [selectedCards, setSelectedCards] = useState([]);

    const handleCardClick = (index,p) => {
      if(p!==gameData.player_id || turn!==gameData.player_id) return
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
          {handcards[playerIndex].map((card, i) => (
          <div key={i}>
            {console.log(handcards,card,i)}
            <img src={gameData.player_id === playerIndex ? require(`./cards/card_${suit[card[1]]}_${card[0] === 13 ? 13 : card[0] % 13}.png`)
                  : require('./cards/card_back.png')} alt="card" 
                  className={(selectedCards.includes(i)) ? 'selected' : ''}
                  onClick={() => handleCardClick(i,playerIndex)}/>
          </div>))
          }
        </div>
      );
    };

    function lastCard(){
      return (
        <div className={'last'}>
          {last&&last.map((card, i) => (
          <div key={i}>
            <img src={require(`./cards/card_${suit[card[1]]}_${card[0] === 13 ? 13 : card[0] % 13}.png`)} alt="card" />
          </div>))
          }
        </div>
      );
    };
    const handlePass = async () => {
      try {
        const response = await fetch(link + '/skip', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            'game_id': gameData.game_id,
            'player_id': gameData.player_id
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          setTurn(data.turn)
        }
      } catch (error) {
        // Handle network error or other exceptions
        console.error('Pass failed', error);
      }
    };
    const handlePlay = async () => {
      try {
        const response = await fetch(link + '/play', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            'game_id': gameData.game_id,
            'player_id': gameData.player_id,
            'cards':selectedCards
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          setTurn(data.turn)
          setLast(data.last)
          setHandcards(data.cards)
        }
      } catch (error) {
        // Handle network error or other exceptions
        console.error('Play failed', error);
      }
    };
  
    return (
      <div className="App">
        {gameState === 'notStarted' && <button onClick={startGame}>Start Game{gameData!==null?gameData.game_id:'noid'}</button>}
        {gameState === 'waiting' && <div>Waiting for game...</div>}
        {gameState === 'inProgress' && (
          
          <div className='table'>
            {renderCardArea((gameData.player_id + 3) % 4)}
            <div className='table2'>
            {renderCardArea((gameData.player_id + 2) % 4)}
            {lastCard()}
            {turn===gameData.player_id&&<div className="buttonrow">
              <button onClick={handlePlay}>Play</button>
              <button onClick={handlePass}>Pass</button>
            </div>}
            {renderCardArea(gameData.player_id)}
            </div>
            {renderCardArea((gameData.player_id + 1) % 4)} 
          </div>
            
        )}
      </div>
    );
  }
  
  export default App;
import React, { useState, useEffect } from 'react';
import './App.css';

function Timebar({ updateTimeLeft }) {
  const [timeLeft, setTimeLeft] = useState(15);

  useEffect(() => {
    const timer = setInterval(() => {
      const newTimeLeft = updateTimeLeft();
      setTimeLeft(newTimeLeft);
    }, 100);  // Update every 100ms for smoother animation

    return () => clearInterval(timer);
  }, [updateTimeLeft]);

  return (
    <div className="App">
      <div className="time-bar" style={{ width: `${(timeLeft / 15) * 100}%` }}></div>
    </div>
  );
}

export default Timebar;
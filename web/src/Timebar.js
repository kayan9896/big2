import React, { useState, useEffect } from 'react';
import './App.css'; // Assuming a CSS file for styling

function Timebar({skip}) {
  const [timeLeft, setTimeLeft] = useState(15); // Time limit in seconds

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prevTime) => {
        if (prevTime > 0) {
          return prevTime - 1;
        } else {
            if (skip&&timeLeft===0) skip()
          clearInterval(timer); // Stop the timer when timeLeft reaches 0
          return 0; // Return 0 to prevent negative time
        }
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [skip]);


  return (
    <div className="App">
      <div className="time-bar" style={{ width: `${(timeLeft / 15) * 100}%` }}></div>
    </div>
  );
}

export default Timebar;

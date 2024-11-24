import React, { useState, useEffect } from 'react';
import './App.css';

function Timebar({ updateTimeLeft }) {
  const [timeLeft, setTimeLeft] = useState(15);
  const [prevTime, setPrevTime] = useState(null);

  useEffect(() => {
    let frameId;
    let lastTimestamp = performance.now();

    const animate = (timestamp) => {
      const deltaTime = timestamp - lastTimestamp;
      
      if (deltaTime >= 50) {  // Update every 50ms
        const newTimeLeft = updateTimeLeft();
        
        // Ensure time only decreases
        if (prevTime === null || newTimeLeft < prevTime) {
          setTimeLeft(newTimeLeft);
          setPrevTime(newTimeLeft);
        }
        
        lastTimestamp = timestamp;
      }
      
      frameId = requestAnimationFrame(animate);
    };

    frameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameId);
  }, [updateTimeLeft, prevTime]);

  const percentage = (timeLeft / 15) * 100;

  return (
    <div className="App">{console.log(percentage)}
      <div className="time-bar" style={{ width: `${percentage}%`,transition: 'width 50ms linear' }}></div>
      <div>{percentage}</div>
    </div>
  );
}
export default Timebar;
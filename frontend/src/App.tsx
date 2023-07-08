import { useState } from 'react'
import './App.css'
import Button from '@mui/material/Button';

function App() {
  const [hello, setHello] = useState([]);

  const handleClick = () => {
    fetch('http://localhost:8000')
      .then(res => res.json())
      .then(data => {
        setHello(data["smile"]);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  };

  return (
    <>
      <h1>笑顔きりとり君</h1>
      <div className="card">
        <Button variant="contained" onClick={handleClick}>
          {hello.length ? hello : (<div>笑顔</div>)}
        </Button>
      </div>
    </>
  );
}

export default App;

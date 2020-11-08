import logo from './logo.svg';
import { useEffect, useState } from 'react';
import ListGroup from 'react-bootstrap/ListGroup';
import Button from 'react-bootstrap/Button';
import './App.css';

function App() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    const requestOptionsGet = {
      method: 'POST',
      body: JSON.stringify({ "command": "refresh"})
    };
    fetch("http://localhost:9998/", requestOptionsGet)
      .then(res => res.json().then((result) => {
        setItems(result);
        console.log(items);
      })
    )
  }, [])

  const handleClick = (itemName, command) => {
    console.log(itemName, command);
    const requestOptions = {
      method: 'POST',
      body: JSON.stringify({ command, "args": [itemName], "with_refresh": true })
    };
    fetch('http://localhost:9998/', requestOptions)
        .then(response => {
          response.json().then((data) => {
            setItems(data);
          })
        })
    }
  

  return (
    <div className="App">
      <header className="App-header">
        <p>
          Welcome to TASKMASTER
        </p>
      </header>
      <div className="Tasks-Panel">
        <div className="Tasks-Daemon-Button">
          <Button variant="outline-primary" onClick={(e) => handleClick("daemon", "stop_daemon")}>Stop daemon</Button>
          <Button variant="outline-primary" onClick={(e) => handleClick("config", "update")}>Update configuration file</Button>
        </div>
        <ListGroup>
          <h3 style={{ color: "#31E981" }}>
            Processes
          </h3>
            {items &&
              items.map(item => {
                return (
                  <ListGroup.Item className="Task-listgroup">
                    {item.task} | {item.uptime} <br />
                    Attached PIDS {item.pids.map((pid) => {
                      return (<p style={{"display": "inline-block"}}>|{pid}|</p>);
                    })} <br />
                    <Button variant="outline-primary" onClick={(e) => handleClick(item.task, "start")}>Start</Button>
                    <Button variant="outline-primary" onClick={(e) => handleClick(item.task, "restart")}>Restart</Button>
                    <Button variant="outline-primary" onClick={(e) => handleClick(item.task, "stop")}>Stop</Button>
                  </ListGroup.Item>
                );
              })}
          </ListGroup>
      </div>
    </div>
  );
}

export default App;

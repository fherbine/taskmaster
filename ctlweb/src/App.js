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
      body: JSON.stringify({ command, "args": command === "stop_daemon" ? [] : [itemName], "with_refresh": command === "stop_daemon" ? false : true })
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
          Welcome to TASKMASTER
      </header>
      <div className="Tasks-Panel">
        <div className="Tasks-Daemon-Button">
          <Button variant="outline-primary" onClick={(e) => handleClick("daemon", "stop_daemon")}>Stop daemon</Button>
          <Button variant="outline-primary" onClick={(e) => handleClick("config", "update")}>Update configuration file</Button>
        </div>
        <ListGroup>
          <h3>
            Processes Name | Uptime | Attached pids
          </h3>
            {items &&
              items.map(item => {
                return (
                  <ListGroup.Item className="Task-listgroup">
                    <div className="taskName">
                      {item.task}
                    </div>
                    <div className="uptimeTask">
                      {item.uptime}
                    </div>
                    <div className="pidsTask">
                      <div className="pids">
                        {item.pids.map((pid) => {
                          return (
                            <div style={{"marginRight": "10px"}}>
                              <p style={{"display": "inline-block", "marginBottom": "0"}}>{pid}</p>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                    <div className="buttonsTask">
                      <Button variant="outline-primary" onClick={(e) => handleClick(item.task, "start")}>Start</Button>
                      <Button variant="outline-primary" onClick={(e) => handleClick(item.task, "restart")}>Restart</Button>
                      <Button variant="outline-primary" onClick={(e) => handleClick(item.task, "stop")}>Stop</Button>
                    </div>
                  </ListGroup.Item>
                );
              })}
          </ListGroup>
      </div>
    </div>
  );
}

export default App;

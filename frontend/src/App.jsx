import { useState } from 'react'
import reactLogo from './assets/react.svg'
import './App.css'
import Graph from './components/Graph'

function App() {
  const [count, setCount] = useState(0)

  return (   
    <>
    <h1>Besso Digital d'una Xarxa de Trànsit</h1>
   
      <div className="App">
        <Graph />
      </div>
      </>
  )
}

export default App

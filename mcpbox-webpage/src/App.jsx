import { useState } from 'react'
import Chatbot from './components/Chatbot.jsx'
import './App.css'

function App() {

  return (
	    <div class="flex justify-center items-center h-screen w-screen">
        <div class="bg-blue-500 text-white p-8 rounded">
          <Chatbot/>
        </div>
      </div>
  )
}

export default App

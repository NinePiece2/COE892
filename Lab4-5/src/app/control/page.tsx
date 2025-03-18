"use client";
import React, { useState, useEffect, useRef } from 'react';

const ControlPage: React.FC = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const [command, setCommand] = useState<string>('');
  const wsRef = useRef<WebSocket | null>(null);
  const roverId = 1; // Adjust this as needed.
  
  // Using the current window host (assuming your FastAPI backend is accessible via the same domain)
  const WS_URL = `ws://${window.location.host}/ws/rover/${roverId}`;

  useEffect(() => {
    wsRef.current = new WebSocket(WS_URL);
    wsRef.current.onopen = () => {
      setMessages((prev) => [...prev, 'Connected to WebSocket']);
    };
    wsRef.current.onmessage = (event) => {
      setMessages((prev) => [...prev, `Server: ${event.data}`]);
    };
    wsRef.current.onerror = (err) => {
      setMessages((prev) => [...prev, `Error: ${err}`]);
    };
    wsRef.current.onclose = () => {
      setMessages((prev) => [...prev, 'Disconnected from WebSocket']);
    };

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [WS_URL]);

  const sendCommand = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(command);
      setMessages((prev) => [...prev, `Sent: ${command}`]);
      setCommand('');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto bg-white shadow-md rounded p-8">
        <h1 className="text-2xl font-bold mb-4">Real-Time Rover Control</h1>
        <div className="flex items-center space-x-4 mb-4">
          <input
            type="text"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            placeholder="Enter command (L, R, M, D)"
            className="border rounded p-2 flex-grow"
          />
          <button
            onClick={sendCommand}
            className="px-4 py-2 bg-indigo-500 text-white rounded hover:bg-indigo-600"
          >
            Send Command
          </button>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-2">Messages</h2>
          <ul className="list-disc list-inside space-y-1">
            {messages.map((msg, idx) => (
              <li key={idx} className="text-gray-700">{msg}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ControlPage;

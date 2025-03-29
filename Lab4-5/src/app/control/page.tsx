"use client";
import React, { useState, useEffect, useRef } from "react";

const NEXT_PUBLIC_WS_BASE_URL = process.env.NEXT_PUBLIC_WS_BASE_URL || `ws://${window.location.host}`;

const ControlPage: React.FC = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const roverId = 1;
  const [wsUrl, setWsUrl] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      //setWsUrl(`/api/ws/ws/rover/${roverId}`);
      //setWsUrl(`ws://${window.location.host}/ws/rover/${roverId}`);
      //setWsUrl(`ws://localhost:8000/ws/rover/${roverId}`);
      setWsUrl(`${NEXT_PUBLIC_WS_BASE_URL}/ws/rover/${roverId}`);
    }
  }, []);

  useEffect(() => {
    if (!wsUrl) return;

    wsRef.current = new WebSocket(wsUrl);
    wsRef.current.onopen = () => setMessages((prev) => [...prev, "Connected to WebSocket"]);
    wsRef.current.onmessage = (event) => setMessages((prev) => [...prev, `Server: ${event.data}`]);
    wsRef.current.onerror = (err) => setMessages((prev) => [...prev, `Error: ${err}`]);
    wsRef.current.onclose = () => setMessages((prev) => [...prev, "Disconnected from WebSocket"]);

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [wsUrl]);

  const handleKeyDown = (event: KeyboardEvent) => {
    const validKeys = ["L", "R", "M", "D"];
    const key = event.key.toUpperCase();
    console.log("Key pressed:", key);
    
    if (validKeys.includes(key)) {
      sendCommand(key);
    }
  };

  const sendCommand = (command: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(command);
      setMessages((prev) => [...prev, `Sent: ${command}`]);
    }
  };

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <div className="80vh p-6">
      <div className="max-w-2xl mx-auto bg-white shadow-md rounded p-8">
        <h1 className="text-2xl font-bold mb-4">Real-Time Rover Control</h1>
        <p className="mb-4 text-gray-600">Press L, R, M, or D on your keyboard to send commands.</p>
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
"use client";
import React, { useState, useEffect, useRef } from "react";

interface Rover {
  id: number;
  status: string;
  position: number[];
  commands: string;
  output?: string[];
  message?: string;
}

const ControlPage: React.FC = () => {
  const [rovers, setRovers] = useState<Rover[]>([]);
  const [selectedRoverId, setSelectedRoverId] = useState<number | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const [wsUrl, setWsUrl] = useState<string | null>(null);
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);

  const fetchRovers = async () => {
    const res = await fetch(`/api/proxy/rovers`);
    const data = await res.json();
    setRovers(data);
  };

  useEffect(() => {
    fetchRovers();
  }, []);

  useEffect(() => {
    if (selectedRoverId !== null) {
      const baseUrl =
        process.env.NEXT_PUBLIC_WS_BASE_URL || `ws://${window.location.host}`;
      const url = `${baseUrl}/ws/rover/${selectedRoverId}`;
      const updatedUrl = url.replace(/^ws:\/\//, (match) =>
        url.includes(".com") || url.includes(".net") ? "wss://" : match
      );
      setWsUrl(updatedUrl);
    }
  }, [selectedRoverId]);

  useEffect(() => {
    if (!wsUrl) return;
    wsRef.current = new WebSocket(wsUrl);
    wsRef.current.onopen = () => addMessage("Connected to WebSocket");
    wsRef.current.onmessage = (event) => addMessage(`Server: ${event.data}`);
    wsRef.current.onerror = (err) => addMessage(`Error: ${err}`);
    wsRef.current.onclose = () => addMessage("Disconnected from WebSocket");

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [wsUrl]);

  // Auto-scroll
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop =
        messagesContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const addMessage = (msg: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setMessages((prev) => [...prev, `[${timestamp}] ${msg}`]);
  };

  const handleKeyDown = (event: KeyboardEvent) => {
    const validKeys = ["L", "R", "M", "D"];
    const key = event.key.toUpperCase();
    if (validKeys.includes(key)) {
      sendCommand(key);
    }
  };

  const sendCommand = (command: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(command);
      addMessage(`Client: ${command}`);
    }
  };

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Handler for when a rover is selected.
  const handleSelectRover = (id: number) => {
    setSelectedRoverId(id);
    setMessages([]); // Clear any old messages.
  };

  return (
    <div className="80vh p-6">
      <div className="max-w-2xl mx-auto bg-white shadow-md rounded p-8">
        <h1 className="text-2xl font-bold mb-4">Real-Time Rover Control</h1>
        {!selectedRoverId ? (
          <>
            {rovers.length === 0 ? (
              <p className="mb-4 text-gray-600">
                No rovers available. Please add a rover first.
              </p>
            ) : (
              <>
                <p className="mb-4 text-gray-600">
                  Select a rover to control. Only rovers with status "Not Started"
                  or "Finished" are selectable.
                </p>
                <ul className="space-y-2">
                  {rovers.map((rover) => {
                    const selectable =
                      rover.status === "Not Started" ||
                      rover.status === "Finished";
                    return (
                      <li
                        key={rover.id}
                        className="p-4 bg-gray-100 rounded flex justify-between items-center"
                      >
                        <span>
                          <strong>ID:</strong> {rover.id} –{" "}
                          <strong>Status:</strong> {rover.status}
                        </span>
                        <button
                          onClick={() => selectable && handleSelectRover(rover.id)}
                          disabled={!selectable}
                          className={`px-3 py-1 rounded ${
                            selectable
                              ? "bg-green-500 hover:bg-green-600 cursor-pointer"
                              : "bg-gray-400 cursor-not-allowed"
                          }`}
                        >
                          {selectable ? "Select" : "Unavailable"}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </>
            )}
          </>
        ) : (
          <>
            <p className="mb-4 text-gray-600">
              Connected to rover with ID: {selectedRoverId}
            </p>
            <p className="mb-4 text-gray-600">
              Press L, R, M, or D on your keyboard to send commands.
            </p>
            <div
              className="border p-4 rounded h-64 overflow-y-auto bg-gray-50"
              ref={messagesContainerRef}
            >
              <ul className="space-y-1">
                {messages.map((msg, idx) => {
                  const alignmentClass = msg.startsWith("[") && msg.includes("Sent:")
                    ? "text-right"
                    : "text-left";
                  return (
                    <li key={idx} className={`whitespace-pre-wrap ${alignmentClass} text-gray-700`}>
                      {msg}
                    </li>
                  );
                })}
              </ul>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ControlPage;
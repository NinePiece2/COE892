"use client";
import React, { useState, useEffect } from 'react';

interface Rover {
  id: number;
  status: string;
  position: number[];
  commands: string;
}

const RoversPage: React.FC = () => {
  const [rovers, setRovers] = useState<Rover[]>([]);
  const [newRoverCmd, setNewRoverCmd] = useState<string>('');

  const fetchRovers = async () => {
    const res = await fetch(`/api/proxy/rovers`);
    const data = await res.json();
    setRovers(data);
  };

  useEffect(() => {
    fetchRovers();
  }, []);

  const createRover = async () => {
    await fetch(`/api/proxy/rovers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        commands: newRoverCmd,
        status: 'Not Started',
        position: [0, 0],
      }),
    });
    fetchRovers();
  };

  const dispatchRover = async (id: number) => {
    await fetch(`/api/proxy/rovers/${id}/dispatch`, { method: 'POST' });
    fetchRovers();
  };

  const deleteRover = async (id: number) => {
    await fetch(`/api/proxy/rovers/${id}`, { method: 'DELETE' });
    fetchRovers();
  };

  return (
    <div className="80vh p-6">
      <div className="max-w-3xl mx-auto bg-white shadow-md rounded p-8">
        <h1 className="text-2xl font-bold mb-4">Rovers Management</h1>
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Create New Rover</h2>
          <div className="flex items-center space-x-4">
            <input
              type="text"
              placeholder="Enter commands"
              value={newRoverCmd}
              onChange={(e) => setNewRoverCmd(e.target.value)}
              className="border rounded p-2 w-full"
            />
            <button
              onClick={createRover}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Create Rover
            </button>
          </div>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-2">All Rovers</h2>
          <ul className="space-y-4">
            {rovers.map((rover) => (
              <li
                key={rover.id}
                className="p-4 bg-gray-100 rounded flex flex-col md:flex-row justify-between items-center"
              >
                <div>
                  <p>
                    <strong>ID:</strong> {rover.id}
                  </p>
                  <p>
                    <strong>Status:</strong> {rover.status}
                  </p>
                  <p>
                    <strong>Position:</strong> {JSON.stringify(rover.position)}
                  </p>
                  <p>
                    <strong>Commands:</strong> {rover.commands}
                  </p>
                </div>
                <div className="flex space-x-2 mt-2 md:mt-0">
                  <button
                    onClick={() => dispatchRover(rover.id)}
                    className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                  >
                    Dispatch
                  </button>
                  <button
                    onClick={() => deleteRover(rover.id)}
                    className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default RoversPage;

"use client";
import React, { useState, useEffect } from 'react';

interface Mine {
  id: number;
  x: number;
  y: number;
  serial_number: string;
}

const MinesPage: React.FC = () => {
  const [mines, setMines] = useState<Mine[]>([]);
  const [newMine, setNewMine] = useState<Omit<Mine, 'id'>>({
    x: 0,
    y: 0,
    serial_number: '',
  });

  // Use the proxied API URL (no need for API_BASE_URL since proxying is done by Next.js)
  const fetchMines = async () => {
    const res = await fetch(`/api/proxy/mines`);
    const data = await res.json();
    setMines(data);
  };

  useEffect(() => {
    fetchMines();
  }, []);

  const createMine = async () => {
    await fetch(`/api/proxy/mines`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newMine),
    });
    fetchMines();
  };

  const deleteMine = async (id: number) => {
    await fetch(`/api/proxy/mines/${id}`, { method: 'DELETE' });
    fetchMines();
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-3xl mx-auto bg-white shadow-md rounded p-8">
        <h1 className="text-2xl font-bold mb-4">Mines Management</h1>
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Create New Mine</h2>
          <div className="space-y-4">
            <div>
              <label className="block">
                X:
                <input
                  type="number"
                  value={newMine.x}
                  onChange={(e) =>
                    setNewMine({ ...newMine, x: parseInt(e.target.value) })
                  }
                  className="border rounded p-1 ml-2"
                />
              </label>
            </div>
            <div>
              <label className="block">
                Y:
                <input
                  type="number"
                  value={newMine.y}
                  onChange={(e) =>
                    setNewMine({ ...newMine, y: parseInt(e.target.value) })
                  }
                  className="border rounded p-1 ml-2"
                />
              </label>
            </div>
            <div>
              <label className="block">
                Serial Number:
                <input
                  type="text"
                  value={newMine.serial_number}
                  onChange={(e) =>
                    setNewMine({ ...newMine, serial_number: e.target.value })
                  }
                  className="border rounded p-1 ml-2"
                />
              </label>
            </div>
            <button
              onClick={createMine}
              className="mt-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Create Mine
            </button>
          </div>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-2">All Mines</h2>
          <ul className="space-y-2">
            {mines.map((mine) => (
              <li
                key={mine.id}
                className="p-4 bg-gray-100 rounded flex justify-between items-center"
              >
                <span>
                  <strong>ID:</strong> {mine.id} – Coordinates: ({mine.x}, {mine.y}) – Serial: {mine.serial_number}
                </span>
                <button
                  onClick={() => deleteMine(mine.id)}
                  className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default MinesPage;

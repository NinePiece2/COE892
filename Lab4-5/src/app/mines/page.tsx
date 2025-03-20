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
  const [error, setError] = useState<string | null>(null);
  const [width, setWidth] = useState<number>(10);
  const [height, setHeight] = useState<number>(10);

  // Define bounds for coordinates
  const MIN_X = 0;
  const MIN_Y = 0;
  const SERIAL_LENGTH = 10;

  const fetchMines = async () => {
    const res = await fetch(`/api/proxy/mines`);
    const data = await res.json();
    setMines(data);

    await fetch(`/api/proxy/map`)
      .then((res) => res.json())
      .then((data) =>{
          setWidth(data[0].length),
          setHeight(data.length)
        })
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    fetchMines();
  }, []);

  const validateInput = () => {
    if (newMine.x < MIN_X || newMine.x > width - 1) {
      setError(`X coordinate must be between ${MIN_X} and ${width - 1}`);
      return false;
    }
    if (newMine.y < MIN_Y || newMine.y > height - 1) {
      setError(`Y coordinate must be between ${MIN_Y} and ${height - 1}`);
      return false;
    }
    if (newMine.serial_number.length !== SERIAL_LENGTH) {
      setError(`Serial number must be exactly ${SERIAL_LENGTH} characters long`);
      return false;
    }
    setError(null);
    return true;
  };

  const createMine = async () => {
    if (!validateInput()) return;

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
    <div className="min-h-screen p-6">
      <div className="max-w-3xl mx-auto bg-white shadow-md rounded p-8">
        <h1 className="text-2xl font-bold mb-4">Mines Management</h1>
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Create New Mine</h2>
          {error && <p className="text-red-500 mb-2">{error}</p>}
          <div className="space-y-4">
            <div>
              <label className="block">
                X:
                <input
                  type="number"
                  value={newMine.x}
                  onChange={(e) =>
                    setNewMine({ ...newMine, x: parseInt(e.target.value) || 0 })
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
                    setNewMine({ ...newMine, y: parseInt(e.target.value) || 0 })
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

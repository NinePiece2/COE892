"use client";
import React, { useState, useEffect } from 'react';

const MapPage: React.FC = () => {
  const [map, setMap] = useState<number[][]>([]);
  const [width, setWidth] = useState<number>(10);
  const [height, setHeight] = useState<number>(10);

  useEffect(() => {
    fetch(`/api/proxy/map`)
      .then((res) => res.json())
      .then((data) => setMap(data))
      .catch((err) => console.error(err));
  }, []);

  const updateMap = async () => {
    const res = await fetch(`/api/proxy/map`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ width, height }),
    });
    const data = await res.json();
    setMap(data.map);
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto bg-white shadow-md rounded p-8">
        <h1 className="text-2xl font-bold mb-4">Field Map</h1>
        <div className="overflow-auto">
          {map && map.length > 0 ? (
            <table className="min-w-full border-collapse">
              <tbody>
                {map.map((row, i) => (
                  <tr key={i}>
                    {row.map((cell, j) => (
                      <td key={j} className="border p-2 text-center">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>Loading map...</p>
          )}
        </div>
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-2">Update Map Dimensions</h2>
          <div className="flex space-x-4 items-center">
            <label>
              <span className="mr-2">Width:</span>
              <input
                type="number"
                className="border rounded p-1"
                value={width}
                onChange={(e) => setWidth(parseInt(e.target.value))}
              />
            </label>
            <label>
              <span className="mr-2">Height:</span>
              <input
                type="number"
                className="border rounded p-1"
                value={height}
                onChange={(e) => setHeight(parseInt(e.target.value))}
              />
            </label>
            <button
              onClick={updateMap}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Update Map
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapPage;

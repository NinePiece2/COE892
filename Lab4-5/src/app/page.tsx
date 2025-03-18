import Link from 'next/link';
import React from 'react';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-xl mx-auto bg-white shadow-lg rounded-lg p-8">
        <h1 className="text-3xl font-bold mb-6 text-center">Operator Dashboard</h1>
        <ul className="space-y-4">
          <li>
            <Link className="block p-4 bg-blue-500 text-white rounded hover:bg-blue-600" href="/map">
              Field Map
            </Link>
          </li>
          <li>
            <Link className="block p-4 bg-green-500 text-white rounded hover:bg-green-600" href="/mines">
              Mines
            </Link>
          </li>
          <li>
            <Link className="block p-4 bg-purple-500 text-white rounded hover:bg-purple-600" href="/rovers">
              Rovers
            </Link>
          </li>
          <li>
            <Link className="block p-4 bg-red-500 text-white rounded hover:bg-red-600" href="/control">
              Real-Time Control
            </Link>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Home;

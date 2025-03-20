'use client';

import React from 'react';
import Link from 'next/link';

const Header = () => {
  return (
    <header className="text-gray-400  body-font">
      <div className="container mx-auto flex flex-wrap p-5 flex-col md:flex-row items-center">
        <nav className="md:ml-auto md:mr-auto flex flex-wrap items-center text-base justify-center">
          <Link className="mr-5 hover:text-white cursor-pointer" href="/" style={{padding: "10px"}}>Home</Link>
          <Link className="mr-5 bg-blue-500 hover:text-white cursor-pointer" href="/map" style={{padding: "10px"}}>Field Map</Link>
          <Link className="mr-5 bg-green-500 hover:text-white cursor-pointer" href="/mines" style={{padding: "10px"}}>Mines</Link>
          <Link className="mr-5 bg-purple-500 hover:text-white cursor-pointer" href="/rovers" style={{padding: "10px"}}>Rovers</Link>
          <Link className="mr-5 bg-red-500 hover:text-white cursor-pointer" href="/control" style={{padding: "10px"}}>Real-Time control</Link>
        </nav>
        
      </div>
    </header>
  );
};

export default Header;

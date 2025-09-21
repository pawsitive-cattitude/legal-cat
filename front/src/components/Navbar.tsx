import React from "react";

const Navbar = () => {
  return (
    <nav className="absolute top-0 left-0 right-0 z-10 flex justify-between items-center px-16 py-6">
      <a href="/" className="flex items-center">
        <div className="flex items-center space-x-2 ml-8">
          <h1 className="text-4xl font-serif text-gray-800">Legal Cat</h1>
          <span className="">
            <img src="/logo.svg" alt="Legal Cat" className="w-10 h-10" />
          </span>
        </div>
      </a>
      <div className="flex space-x-16 ml-16 mr-32">
        <a
          href="/analyze"
          className="text-gray-700 hover:text-gray-900 font-large"
        >
          Analysis
        </a>
        <a
          href="#services"
          className="text-gray-700 hover:text-gray-900 font-large"
        >
          Services
        </a>
        <a
          href="#about"
          className="text-gray-700 hover:text-gray-900 font-large"
        >
          About Us
        </a>
        <a
          href="#contact"
          className="text-gray-700 hover:text-gray-900 font-large"
        >
          Contact
        </a>
      </div>
    </nav>
  );
};

export default Navbar;

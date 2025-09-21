import React from "react";
import { Phone } from "lucide-react";
import Navbar from "../components/Navbar";

const LegalCatHomepage = () => {
  return (
    <div className="min-h-screen" style={{ backgroundColor: "#F7F2E5" }}>
      <Navbar />

      {/* Hero Section */}
      <section
        className="relative h-screen flex items-center pl-16"
        style={{
          backgroundImage: "url(cat.png)",
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      >
        <div className="max-w-2xl ml-8">
          <h2 className="text-6xl font-serif text-gray-800 leading-tight mb-8">
            Navigating the Legal
            <br />
            Landscape with
            <br />
            Feline Finesse
          </h2>
          <button className="bg-gray-800 text-white px-8 py-4 rounded-full text-lg font-medium hover:bg-gray-700 transition-colors">
            Get Started
          </button>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="px-16 py-20">
        <div className="max-w-7xl">
          <div className="text-left mb-16">
            <h3 className="text-4xl font-serif text-gray-800 mb-4">Services</h3>
            <p className="text-gray-600 max-w-md">
              Lorem ipsum dolor sit amet, consectetur,
              <br />
              adipiscing elit, sed do eiusmod
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-16 text-center max-w-4xl">
            <div className="space-y-4">
              <div className="w-16 h-16 mx-auto rounded-lg flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <h4 className="text-xl font-serif text-gray-800">Legal Advice</h4>
            </div>

            <div className="space-y-4">
              <div className="w-16 h-16 mx-auto rounded-lg flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"
                  />
                </svg>
              </div>
              <h4 className="text-xl font-serif text-gray-800">Legal Cases</h4>
            </div>

            <div className="space-y-4">
              <div className="w-16 h-16 mx-auto rounded-lg flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"
                  />
                </svg>
              </div>
              <h4 className="text-xl font-serif text-gray-800">Legal Issues</h4>
            </div>
          </div>
        </div>
      </section>

      {/* About Us & Contact Section */}
      <section className="px-16 py-20">
        <div className="max-w-7xl grid md:grid-cols-2 gap-32">
          {/* About Us */}
          <div className="text-left">
            <h3 className="text-4xl font-serif text-gray-800 mb-4">About Us</h3>
            <p className="text-gray-600 max-w-md">
              Lorem ipsum dolor sit amet, consectetur,
              <br />
              adipiscing elit, sed do eiusmod tempor incididunt
            </p>
          </div>

          {/* Contact */}
          <div className="text-left">
            <h3 className="text-4xl font-serif text-gray-800 mb-8">Contact</h3>
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 rounded-full overflow-hidden">
                <img
                  src="/api/placeholder/64/64"
                  alt="Team"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="text-left">
                <p className="font-medium text-gray-800">Vowel Cat</p>
                <div className="flex items-center text-gray-600 text-sm">
                  <Phone className="w-4 h-4 mr-1" />
                  +91-123-456-789
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LegalCatHomepage;

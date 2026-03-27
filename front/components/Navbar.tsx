"use client";

import Link from "next/link";
import { useState } from "react";
import { FaUserCircle } from "react-icons/fa";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <nav className="flex justify-between items-center p-4 bg-black shadow relative">
      {/* Logo en vert */}
      <Link href="/">
        <h1 className="font-bold text-green-500 cursor-pointer hover:text-green-400">
          Ease Book
        </h1>
      </Link>

      {/* Profil icon */}
      <div className="relative">
        <button
          onClick={() => setOpen(!open)}
          className="text-white text-2xl focus:outline-none"
        >
          <FaUserCircle />
        </button>

        {/* Dropdown */}
        {open && (
          <div className="absolute right-0 mt-2 w-40 bg-black rounded-lg shadow-lg py-2 z-50">
            <Link
              href="/login"
              className="block px-4 py-2 text-green-500 hover:bg-black rounded"
              onClick={() => setOpen(false)}
            >
              Login
            </Link>
            <Link
              href="/register"
              className="block px-4 py-2 text-green-500 hover:bg-black rounded"
              onClick={() => setOpen(false)}
            >
              Inscription
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
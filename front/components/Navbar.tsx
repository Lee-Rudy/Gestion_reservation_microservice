"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { FaUserCircle } from "react-icons/fa";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState("");
  const router = useRouter();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("token");
    const userStr = localStorage.getItem("user");
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        setIsLoggedIn(true);
        setUserEmail(user.email);
      } catch {
        setIsLoggedIn(false);
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setIsLoggedIn(false);
    setOpen(false);
    router.push("/");
  };

  return (
    <nav className="flex justify-between items-center p-4 bg-black shadow relative">
      <Link href="/">
        <h1 className="font-bold text-green-500 cursor-pointer hover:text-green-400">
          Ease Book
        </h1>
      </Link>

      <div className="relative">
        <button
          onClick={() => setOpen(!open)}
          className="text-white text-2xl focus:outline-none"
        >
          <FaUserCircle />
        </button>

        {open && (
          <div className="absolute right-0 mt-2 w-48 bg-neutral-900 border border-neutral-800 rounded-lg shadow-lg py-2 z-50">
            {isLoggedIn ? (
              <>
                <div className="px-4 py-2 text-gray-400 text-sm border-b border-neutral-800">
                  {userEmail}
                </div>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-4 py-2 text-red-400 hover:bg-neutral-800 rounded"
                >
                  Déconnexion
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="block px-4 py-2 text-green-500 hover:bg-neutral-800 rounded"
                  onClick={() => setOpen(false)}
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="block px-4 py-2 text-green-500 hover:bg-neutral-800 rounded"
                  onClick={() => setOpen(false)}
                >
                  Inscription
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
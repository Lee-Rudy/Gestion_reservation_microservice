"use client";

import { useState } from "react";
import Input from "@/components/Input";
import Button from "@/components/Button";
import Link from "next/link";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    if (!email || !password) return alert("Champs requis");
    
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        return alert(error.message || "Erreur de connexion");
      }

      const data = await response.json();
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify({ email, role: data.role }));
      
      if (data.role === "ADMIN") {
        window.location.href = "/admin";
      } else {
        window.location.href = "/reservation";
      }
    } catch (error) {
      alert("Erreur de connexion");
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-black relative">
      {/* Bouton Retour */}
      <Link
        href="/"
        className="absolute left-8 top-1/7 transform -translate-y-1/2 text-green-500 px-4 py-2 rounded-lg shadow hover:bg-gray-900 transition font-semibold"
      >
        ← Retour
      </Link>

      <div className="w-80 p-6 space-y-6 bg-black rounded-2xl shadow-lg text-white border border-gray-900">
        <h2 className="text-2xl font-bold text-center text-green-500">Connexion</h2>

        <div className="space-y-4">
          <Input 
            placeholder="Email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            className="bg-gray-800 text-white border-gray-700 focus:border-green-500"
          />
          <Input 
            type="password" 
            placeholder="Mot de passe" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)}
            className="bg-gray-800 text-white border-gray-700 focus:border-green-500"
          />
          <Button 
            onClick={handleLogin} 
            className="bg-green-500 hover:bg-green-600 text-black w-full"
          >
            Se connecter
          </Button>
        </div>

        <p className="text-center text-sm mt-4 text-gray-300">
          Pas encore inscrit ?{" "}
          <Link href="/register" className="underline text-green-500 hover:text-green-400">
            Créer un compte
          </Link>
        </p>
      </div>
    </div>
  );
}
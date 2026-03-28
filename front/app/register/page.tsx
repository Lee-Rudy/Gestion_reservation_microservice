"use client";

import { useState } from "react";
import Input from "@/components/Input";
import Button from "@/components/Button";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleRegister = async () => {
    if (!name || !email || !password) return alert("Champs requis");
    
    setLoading(true);
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password, role: "USER" }),
      });

      if (!response.ok) {
        const error = await response.json();
        alert(error.message || "Erreur lors de l'inscription");
        return;
      }

      alert("Compte créé avec succès");
      router.push("/login");
    } catch (error) {
      alert("Erreur lors de l'inscription");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-black relative">
      {/* Bouton Retour vers la page Login */}
      <Link
        href="/login"
        className="absolute left-8 top-1/7 transform -translate-y-1/2 text-green-500 px-4 py-2 rounded-lg shadow hover:bg-gray-900 transition font-semibold"
      >
        ← Retour
      </Link>

      <div className="w-80 p-6 space-y-6 bg-black rounded-2xl shadow-lg text-white border border-gray-900">
        <h2 className="text-2xl font-bold text-center text-green-500">Inscription</h2>

        <div className="space-y-4">
          <Input 
            placeholder="Nom" 
            value={name} 
            onChange={(e) => setName(e.target.value)}
            className="bg-gray-800 text-white border-gray-700 focus:border-green-500"
          />
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
            onClick={handleRegister} 
            className="bg-green-500 hover:bg-green-600 text-black w-full"
            disabled={loading}
          >
            {loading ? "Création..." : "Créer un compte"}
          </Button>
        </div>

        <p className="text-center text-sm mt-4 text-gray-300">
          Déjà inscrit ?{" "}
          <Link href="/login" className="underline text-green-500 hover:text-green-400">
            Se connecter
          </Link>
        </p>
      </div>
    </div>
  );
}
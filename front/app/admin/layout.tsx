"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("token");
    const userStr = localStorage.getItem("user");
    
    if (!token || !userStr) {
      router.push("/login");
      return;
    }

    try {
      const user = JSON.parse(userStr);
      if (user.role !== "ADMIN") {
        alert("Accès refusé : administrateur requis");
        router.push("/");
        return;
      }
      setIsAuthorized(true);
    } catch {
      router.push("/login");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/login");
  };

  if (!isAuthorized) {
    return (
      <div className="flex items-center justify-center h-screen bg-black text-white">
        <p className="text-gray-400">Vérification des permissions...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-black text-white">
      
      <aside className="w-64 bg-neutral-900 border-r border-neutral-800 p-6 flex flex-col justify-between">
        <div>
          <h2 className="text-2xl font-bold text-green-400 mb-10">Admin</h2>
          <nav className="flex flex-col space-y-4 text-gray-400">
            <Link href="/admin" className="hover:text-green-400">Dashboard</Link>
            <Link href="/admin/reservation" className="hover:text-green-400">Réservations</Link>
          </nav>
        </div>

        <div>
          <button 
            onClick={handleLogout}
            className="w-full py-2 px-4 bg-gray-600 rounded hover:bg-red-500"
          >
            Déconnexion
          </button>
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-auto">{children}</main>
    </div>
  );
}
"use client";
import Link from "next/link";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-black text-white">
      
      {/* Sidebar */}
      <aside className="w-64 bg-neutral-900 border-r border-neutral-800 p-6 flex flex-col justify-between">
        <div>
          <h2 className="text-2xl font-bold text-green-400 mb-10">Admin</h2>
          <nav className="flex flex-col space-y-4 text-gray-400">
            <Link href="/admin" className="hover:text-green-400">Dashboard</Link>
            <Link href="/admin/reservation" className="hover:text-green-400">Réservations</Link>
          </nav>
        </div>

        {/* Top menu / logout */}
        <div>
          <button className="w-full py-2 px-4 bg-gray-600 rounded hover:bg-red-500">
            Déconnexion
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-8 overflow-auto">{children}</main>
    </div>
  );
}
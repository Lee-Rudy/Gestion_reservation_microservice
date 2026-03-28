"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface Stats {
  users: number;
  reservations: number;
  paiements: number;
}

interface Log {
  id?: number;
  user_email?: string;
  action: string;
  details?: string;
  created_at: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats>({
    users: 0,
    reservations: 0,
    paiements: 0,
  });
  const [logs, setLogs] = useState<Log[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/login");
        return;
      }

      const [statsResponse, logsResponse] = await Promise.all([
        fetch("/api/admin/stats", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("/api/admin/logs", {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (!statsResponse.ok || !logsResponse.ok) {
        alert("Erreur lors du chargement des données");
        return;
      }

      const statsData = await statsResponse.json();
      const logsData = await logsResponse.json();

      setStats(statsData);
      setLogs(logsData);
    } catch (error) {
      alert("Erreur lors du chargement des données");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-gray-400">Chargement...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-3 gap-6">
        <StatBlock title="Utilisateurs" value={stats.users} />
        <StatBlock title="Réservations" value={stats.reservations} />
        <StatBlock title="Paiements" value={stats.paiements} />
      </div>

      {/* LOGS EN TABLEAU */}
      <div className="bg-neutral-900 rounded-2xl p-6 border border-neutral-800 shadow-lg">
        <h2 className="mb-4 text-lg font-semibold">Logs récents</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-black text-gray-400">
              <tr>
                <th className="p-3">Utilisateur</th>
                <th className="p-3">Action</th>
                <th className="p-3">Details</th>
                <th className="p-3">Date / Heure</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-3 text-center text-gray-400">
                    Aucun log disponible
                  </td>
                </tr>
              ) : (
                logs.map((log, index) => (
                  <tr key={index} className="border-t border-neutral-800 hover:bg-black/30 transition">
                    <td className="p-3">{log.user_email || "Systeme"}</td>
                    <td className="p-3">{log.action}</td>
                    <td className="p-3 text-gray-400">{log.details || "-"}</td>
                    <td className="p-3 text-gray-400">{new Date(log.created_at).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatBlock({ title, value }: { title: string; value: number }) {
  return (
    <div className="bg-neutral-800 p-5 rounded-xl border border-green-500/20 shadow">
      <p className="text-gray-400 text-sm">{title}</p>
      <p className="text-2xl font-bold text-green-400 mt-2">{value}</p>
    </div>
  );
}
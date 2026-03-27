"use client";
import { useState } from "react";

type Log = {
  correlation_id: string;
  action: string;
  created_at: string;
};

export default function DashboardPage() {
  const total = 120;
  const enAttente = 25;
  const annulee = 10;

  const logs: Log[] = [
    { correlation_id: "a1b2c3d4-e5f6-7g8h-9i10", action: "Réservation confirmée", created_at: "2026-03-26 10:00" },
    { correlation_id: "b2c3d4e5-f6g7-8h9i-10j1", action: "Paiement validé", created_at: "2026-03-26 09:45" },
    { correlation_id: "c3d4e5f6-g7h8-9i10-11j2", action: "Réservation annulée", created_at: "2026-03-25 16:30" },
    { correlation_id: "d4e5f6g7-h8i9-10j11", action: "Nouvelle réservation", created_at: "2026-03-26 11:20" },
    { correlation_id: "e5f6g7h8-i9j10-11k12", action: "Erreur paiement", created_at: "2026-03-25 15:10" },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      {/* STATS */}
      <div className="grid grid-cols-3 gap-6">
        <StatBlock title="Total Réservations" value={total} />
        <StatBlock title="En attente" value={enAttente} />
        <StatBlock title="Annulées" value={annulee} />
      </div>

      {/* LOGS EN TABLEAU */}
      <div className="bg-neutral-900 rounded-2xl p-6 border border-neutral-800 shadow-lg">
        <h2 className="mb-4 text-lg font-semibold">Logs récents</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-black text-gray-400">
              <tr>
                <th className="p-3">Correlation ID</th>
                <th className="p-3">Action</th>
                <th className="p-3">Date / Heure</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, index) => (
                <tr key={index} className="border-t border-neutral-800 hover:bg-black/30 transition">
                  <td className="p-3">{log.correlation_id}</td>
                  <td className="p-3">{log.action}</td>
                  <td className="p-3 text-gray-400">{log.created_at}</td>
                </tr>
              ))}
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
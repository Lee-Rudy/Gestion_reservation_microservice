"use client";
import { useState } from "react";

type Reservation = {
  id: number;
  client: string;
  date: string;
  status: "confirmé" | "en attente" | "annulé";
};

export default function ReservationsPage() {
  const reservations: Reservation[] = Array.from({ length: 25 }, (_, i) => ({
    id: i + 1,
    client: `Client ${i + 1}`,
    date: `2026-03-${(i % 30) + 1}`,
    status: i % 3 === 0 ? "confirmé" : i % 3 === 1 ? "en attente" : "annulé",
  }));

  const [page, setPage] = useState(1);
  const itemsPerPage = 10;

  const paged = reservations.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage
  );

  const totalPages = Math.ceil(reservations.length / itemsPerPage);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold mb-6">Réservations</h1>

      <div className="bg-neutral-900 rounded-2xl p-6 border border-neutral-800 shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-black text-gray-400">
              <tr>
                <th className="p-3 text-left">ID</th>
                <th className="p-3 text-left">Client</th>
                <th className="p-3 text-left">Date</th>
                <th className="p-3 text-left">Status</th>
              </tr>
            </thead>

            <tbody>
              {paged.map((r) => (
                <tr key={r.id} className="border-t border-neutral-800 hover:bg-black/30">
                  <td className="p-3">{r.id}</td>
                  <td className="p-3">{r.client}</td>
                  <td className="p-3">{r.date}</td>
                  <td className="p-3">
                    <StatusBadge value={r.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex justify-end mt-4 space-x-2">
          <button
            disabled={page === 1}
            onClick={() => setPage(page - 1)}
            className="px-3 py-1 bg-green-600 rounded disabled:opacity-40"
          >
            Prev
          </button>
          <button
            disabled={page === totalPages}
            onClick={() => setPage(page + 1)}
            className="px-3 py-1 bg-green-600 rounded disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ value }: { value: string }) {
  const color =
    value === "confirmé"
      ? "bg-green-600/20 text-green-400"
      : value === "en attente"
      ? "bg-yellow-500/20 text-yellow-400"
      : "bg-red-600/20 text-red-400";

  return <span className={`px-3 py-1 rounded-full text-xs ${color}`}>{value}</span>;
}
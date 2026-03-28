"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface Reservation {
  id: number;
  user_email: string;
  category_name?: string;
  start_date: string;
  end_date: string;
  status: string;
  nb_persons: number;
}

export default function ReservationsPage() {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const router = useRouter();
  const itemsPerPage = 10;

  useEffect(() => {
    loadReservations();
  }, []);

  const loadReservations = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await fetch("/api/reservations", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        alert("Erreur lors du chargement des réservations");
        return;
      }

      const data = await response.json();
      setReservations(data);
    } catch (error) {
      alert("Erreur lors du chargement des réservations");
    } finally {
      setLoading(false);
    }
  };

  const paged = reservations.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage
  );

  const totalPages = Math.ceil(reservations.length / itemsPerPage);

  const getStatusLabel = (status: string) => {
    const statusMap: Record<string, string> = {
      CONFIRMED: "confirmé",
      PENDING: "en attente",
      CANCELLED: "annulé",
    };
    return statusMap[status] || status.toLowerCase();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-gray-400">Chargement...</p>
      </div>
    );
  }

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
                <th className="p-3 text-left">Catégorie</th>
                <th className="p-3 text-left">Date début</th>
                <th className="p-3 text-left">Personnes</th>
                <th className="p-3 text-left">Status</th>
              </tr>
            </thead>

            <tbody>
              {paged.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-3 text-center text-gray-400">
                    Aucune réservation
                  </td>
                </tr>
              ) : (
                paged.map((r) => (
                  <tr key={r.id} className="border-t border-neutral-800 hover:bg-black/30">
                    <td className="p-3">{r.id}</td>
                    <td className="p-3">{r.user_email}</td>
                    <td className="p-3">{r.category_name || "N/A"}</td>
                    <td className="p-3">{new Date(r.start_date).toLocaleString()}</td>
                    <td className="p-3">{r.nb_persons}</td>
                    <td className="p-3">
                      <StatusBadge value={getStatusLabel(r.status)} />
                    </td>
                  </tr>
                ))
              )}
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
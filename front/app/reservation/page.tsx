"use client";

import { useState, useEffect } from "react";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Navbar from "@/components/Navbar";
import { useRouter } from "next/navigation";

interface Category {
  id: number;
  name: string;
  description: string;
  base_price: number;
}

export default function Reservation() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [date, setDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [people, setPeople] = useState(1);
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const router = useRouter();

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await fetch("/api/categories");
      if (response.ok) {
        const data = await response.json();
        const categoriesArray = Array.isArray(data) ? data : [];
        setCategories(categoriesArray);
        if (categoriesArray.length > 0) {
          setCategoryId(categoriesArray[0].id);
        }
      }
    } catch (error) {
      alert("Erreur lors du chargement des catégories");
      setCategories([]);
    } finally {
      setLoadingCategories(false);
    }
  };

  const selectedCategory = Array.isArray(categories) ? categories.find(c => c.id === categoryId) : null;
  const total = selectedCategory ? selectedCategory.base_price * people : 0;

  const handleSubmitReservation = async () => {
    if (!categoryId || !date || !startTime || !endTime) {
      alert("Veuillez remplir tous les champs");
      return;
    }

    setLoading(true);
    try {
      const userStr = localStorage.getItem("user");
      const user = userStr ? JSON.parse(userStr) : null;
      
      if (!user?.email) {
        alert("Veuillez vous connecter");
        router.push("/login");
        return;
      }

      const dateParts = date.split('-');
      const startDateTime = `${date}T${startTime}:00`;
      const nextDay = new Date(date);
      nextDay.setDate(nextDay.getDate() + 1);
      const endDate = nextDay.toISOString().split('T')[0];
      const endDateTime = `${endDate}T${endTime}:00`;

      const payload = {
        category_id: categoryId,
        start_date: startDateTime,
        end_date: endDateTime,
        nb_persons: people,
        user_email: user.email,
        methode: "carte",
        devise: "EUR"
      };

      console.log("Sending reservation:", payload);

      const response = await fetch("/api/reservations/saga", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const error = await response.json();
        console.error("Reservation error:", error);
        console.error("Status:", response.status);
        alert(`Erreur ${response.status}: ${error.message || error.detail || "Erreur lors de la reservation"}`);
        return;
      }

      const result = await response.json();
      console.log("Reservation success:", result);
      alert("Reservation effectuee avec succes !");
      router.push("/");
    } catch (error) {
      console.error("Reservation exception:", error);
      alert("Erreur lors de la reservation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />

      <div className="p-6 max-w-md mx-auto mt-8 space-y-8">
        <h2 className="text-3xl font-bold text-center mb-4">Réservation</h2>

        <div className=" border border-gray-900 rounded-2xl shadow-xl p-6 space-y-6">
          {step === 1 && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Categorie
                </label>
                {loadingCategories ? (
                  <p className="text-center text-gray-400">Chargement des categories...</p>
                ) : categories.length === 0 ? (
                  <p className="text-center text-red-400">Aucune categorie disponible</p>
                ) : (
                  <select
                    value={categoryId || ""}
                    onChange={(e) => setCategoryId(Number(e.target.value))}
                    className="w-full p-3 rounded-xl border border-gray-700 text-black bg-gray-200 focus:outline-none focus:ring-2 focus:ring-green-500 transition"
                  >
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.name} - {cat.base_price}€/jour
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Date
                </label>
                <Input
                  type="date"
                  placeholder="Date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  className="w-full p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-green-500 transition"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Horaires
                </label>
                <div className="flex gap-4">
                  <Input
                    type="time"
                    placeholder="Heure debut"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="flex-1 p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-green-500 transition"
                  />
                  <Input
                    type="time"
                    placeholder="Heure fin"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="flex-1 p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-green-500 transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Nombre de personnes
                </label>
                <Input
                  type="number"
                  placeholder="Nombre de personnes"
                  value={people}
                  onChange={(e) => setPeople(Math.max(1, Number(e.target.value)))}
                  className="w-full p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-green-500 transition"
                />
              </div>

              <Button
                onClick={() => setStep(2)}
                variant="primary"
                className="w-full bg-green-500 text-black rounded-xl py-3 font-semibold hover:bg-green-600 transition"
              >
                Confirmer
              </Button>
            </>
          )}

          {step === 2 && (
            <>
              <h3 className="font-bold text-2xl text-center mb-6 text-green-400">
                Votre devis
              </h3>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between border-b border-green-900 pb-2">
                  <span className="text-green-300">Catégorie</span>
                  <span className="font-semibold text-white">{selectedCategory?.name}</span>
                </div>

                <div className="flex justify-between border-b border-green-900 pb-2">
                  <span className="text-green-300">Date</span>
                  <span className="font-semibold text-white">{date}</span>
                </div>

                <div className="flex justify-between border-b border-green-900 pb-2">
                  <span className="text-green-300">Heure</span>
                  <span className="font-semibold text-white">
                    {startTime} - {endTime}
                  </span>
                </div>

                <div className="flex justify-between border-b border-green-900 pb-2">
                  <span className="text-green-300">Personnes</span>
                  <span className="font-semibold text-white">{people}</span>
                </div>
              </div>

              <div className="flex justify-between items-center mt-6 text-lg">
                <span className="text-green-400 font-semibold">Total</span>
                <span className="text-white font-bold text-xl">{total}€</span>
              </div>

              <div className="flex gap-4 mt-6">
                <Button
                  onClick={() => setStep(1)}
                  variant="outline"
                  className="flex-1 py-3 rounded-xl border-green-700 text-green-300 hover:bg-green-900"
                >
                  Modifier
                </Button>

                <Button
                  onClick={() => setStep(3)}
                  className="flex-1 bg-white text-black rounded-xl py-3 font-semibold hover:bg-gray-200 transition"
                >
                  Paiement
                </Button>
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <h3 className="font-bold text-2xl text-center mb-6 text-green-400">Paiement</h3>

              <p className="text-center text-gray-400 mb-6">
                Montant total : <span className="text-green-400 font-bold text-2xl">{total}€</span>
              </p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Methode de paiement
                  </label>
                  <select
                    className="w-full p-3 rounded-xl border border-gray-700 text-black bg-gray-200 focus:outline-none focus:ring-2 focus:ring-green-500 transition"
                    defaultValue="carte"
                  >
                    <option value="carte">Carte bancaire</option>
                    <option value="paypal">PayPal</option>
                    <option value="virement">Virement</option>
                  </select>
                </div>

                <p className="text-sm text-gray-400 text-center">
                  Le paiement sera traite automatiquement lors de la validation
                </p>
              </div>

              <div className="flex gap-4 mt-6">
                <Button
                  onClick={() => setStep(2)}
                  variant="outline"
                  className="flex-1 py-3 rounded-xl border-green-700 text-green-300 hover:bg-green-900"
                >
                  Retour
                </Button>

                <Button
                  onClick={handleSubmitReservation}
                  disabled={loading}
                  className="flex-1 bg-green-500 text-black rounded-xl py-3 font-semibold hover:bg-green-600 transition"
                >
                  {loading ? "Traitement..." : "Confirmer et payer"}
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
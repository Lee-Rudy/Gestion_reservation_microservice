"use client";

import { useState } from "react";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Navbar from "@/components/Navbar";

export default function Reservation() {
  const [category, setCategory] = useState("Salle");
  const [date, setDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [people, setPeople] = useState(1);
  const [step, setStep] = useState(1); // 1 = formulaire, 2 = devis, 3 = paiement

  const prices: any = {
    Salle: 100,
    Restaurant: 30,
    Hôtel: 80,
  };

  const total = prices[category] * people;

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />

      <div className="p-6 max-w-md mx-auto mt-8 space-y-8">
        <h2 className="text-3xl font-bold text-center mb-4">Réservation</h2>

        <div className=" border border-gray-900 rounded-2xl shadow-xl p-6 space-y-6">
          {step === 1 && (
            <>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full p-3 rounded-xl border border-gray-700 text-black bg-gray-200 focus:outline-none focus:ring-2 focus:ring-white transition"
              >
                <option>Salle</option>
                <option>Restaurant</option>
                <option>Hôtel</option>
              </select>

              <Input
                type="date"
                placeholder="Date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-white transition"
              />

              <div className="flex gap-4">
                <Input
                  type="time"
                  placeholder="Heure début"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="flex-1 p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-white transition"
                />
                <Input
                  type="time"
                  placeholder="Heure fin"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  className="flex-1 p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-white transition"
                />
              </div>

              <Input
                type="number"
                placeholder="Nombre de personnes"
                value={people}
                onChange={(e) => setPeople(Number(e.target.value))}
                className="w-full p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-white transition"
              />

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
                  <span className="font-semibold text-white">{category}</span>
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

              <Input
                placeholder="Nom carte"
                value=""
                onChange={() => {}}
                className="w-full p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-white transition"
              />
              <Input
                placeholder="Numéro carte"
                value=""
                onChange={() => {}}
                className="w-full p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-white transition"
              />
              <Input
                placeholder="Expiration"
                value=""
                onChange={() => {}}
                className="w-full p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-white transition"
              />
              <Input
                placeholder="CVV"
                value=""
                onChange={() => {}}
                className="w-full p-3 rounded-xl border border-gray-700 text-black focus:outline-none focus:ring-2 focus:ring-white transition"
              />

              <div className="flex gap-4 mt-6">
                <Button
                    onClick={() => setStep(2)}
                    variant="outline"
                    className="flex-1 py-3 rounded-xl"
                  >
                    Annuler
                </Button>

                <Button
                  onClick={() => alert("Paiement réussi 🎉")}
                  className="flex-1 bg-white text-black rounded-xl py-3 font-semibold hover:bg-gray-200 transition"
                >
                  Payer
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
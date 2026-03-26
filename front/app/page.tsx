import Navbar from "@/components/Navbar";
import Link from "next/link";

export default function Home() {
  return (
    <div className="bg-black min-h-screen flex flex-col">
      <Navbar />

      {/* Hero full screen */}
      <section className="relative h-screen">
        <img
          src="https://images.pexels.com/photos/262047/pexels-photo-262047.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=1260"
          alt="Réservation"
          className="w-full h-full object-cover brightness-50 grayscale"
        />
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
          <h1 className="text-5xl md:text-6xl font-extrabold text-white-500">
            Réservez facilement en quelques clics
          </h1>
          <p className="text-lg md:text-xl text-gray-200 my-4 max-w-2xl">
            Salle, restaurant ou hôtel, Faites votre réservation.
          </p>
          <Link
            href="/reservation"
            className="bg-green-500 hover:bg-green-600 text-black px-8 py-3 rounded-lg font-semibold transition"
          >
            Réserver maintenant
          </Link>
        </div>
      </section>
    </div>
  );
}
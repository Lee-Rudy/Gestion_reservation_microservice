const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const formData = new FormData();
  formData.append("username", email);
  formData.append("password", password);

  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Email ou mot de passe incorrect");
  }

  return response.json();
}

export async function register(
  name: string,
  email: string,
  password: string,
  role: string = "USER"
): Promise<User> {
  const response = await fetch(`${API_URL}/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password, role }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Erreur lors de l'inscription");
  }

  return response.json();
}

export async function getCategories() {
  const response = await fetch(`${API_URL}/categories`);
  if (!response.ok) throw new Error("Erreur chargement categories");
  return response.json();
}

export async function createReservation(data: {
  category_id: number;
  start_date: string;
  end_date: string;
  nb_persons: number;
  user_email: string;
}) {
  const token = localStorage.getItem("token");
  const response = await fetch(`${API_URL}/reservations/saga`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Erreur reservation");
  }

  return response.json();
}

export async function getReservations(token?: string) {
  const headers: HeadersInit = {};
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_URL}/reservations`, { headers });
  if (!response.ok) throw new Error("Erreur chargement reservations");
  return response.json();
}

export async function getAdminStats(token: string) {
  const response = await fetch(`${API_URL}/admin/stats`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Erreur chargement stats");
  return response.json();
}

export async function getAdminLogs(token: string, limit: number = 50) {
  const response = await fetch(`${API_URL}/admin/logs?limit=${limit}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Erreur chargement logs");
  return response.json();
}

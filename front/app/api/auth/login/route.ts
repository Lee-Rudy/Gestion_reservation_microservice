import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_GATEWAY_URL || "http://api:8000";

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();

    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      return NextResponse.json(
        { message: "Email ou mot de passe incorrect" },
        { status: 401 }
      );
    }

    const data = await response.json();

    const verifyResponse = await fetch(`${API_URL}/auth/verify`, {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });

    let role = "USER";
    if (verifyResponse.ok) {
      const verifyData = await verifyResponse.json();
      role = verifyData.role;
    }

    return NextResponse.json({ ...data, role });
  } catch (error) {
    return NextResponse.json(
      { message: "Erreur serveur" },
      { status: 500 }
    );
  }
}

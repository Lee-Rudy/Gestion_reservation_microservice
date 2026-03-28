import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_GATEWAY_URL || "http://api:8000";

export async function GET(request: NextRequest) {
  try {
    const token = request.headers.get("authorization");

    const response = await fetch(`${API_URL}/reservations`, {
      headers: token ? { Authorization: token } : {},
    });

    if (!response.ok) {
      return NextResponse.json(
        { message: "Erreur chargement reservations" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(Array.isArray(data) ? data : []);
  } catch (error) {
    return NextResponse.json([], { status: 500 });
  }
}

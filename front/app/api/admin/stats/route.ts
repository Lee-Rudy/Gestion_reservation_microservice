import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_GATEWAY_URL || "http://api:8000";

export async function GET(request: NextRequest) {
  try {
    const token = request.headers.get("authorization");
    if (!token) {
      return NextResponse.json({ message: "Non autorise" }, { status: 401 });
    }

    const response = await fetch(`${API_URL}/admin/stats`, {
      headers: { Authorization: token },
    });

    if (!response.ok) throw new Error("Error fetching stats");
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { users: 0, reservations: 0, paiements: 0 },
      { status: 500 }
    );
  }
}

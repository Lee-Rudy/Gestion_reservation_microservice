import { NextResponse } from "next/server";

const API_URL = process.env.API_GATEWAY_URL || "http://api:8000";

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/categories`, {
      signal: AbortSignal.timeout(10000),
    });
    
    if (!response.ok) {
      console.error("Categories API error:", response.status);
      return NextResponse.json([]);
    }
    
    const data = await response.json();
    const categoriesArray = Array.isArray(data) ? data : [];
    
    return NextResponse.json(categoriesArray.map(cat => ({
      id: cat.id,
      name: cat.name,
      description: cat.description || "",
      base_price: cat.price_per_day || 100,
    })));
  } catch (error) {
    console.error("Categories fetch error:", error);
    return NextResponse.json([]);
  }
}

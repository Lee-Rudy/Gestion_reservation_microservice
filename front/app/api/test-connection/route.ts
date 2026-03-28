import { NextResponse } from "next/server";

const API_URL = process.env.API_GATEWAY_URL || "http://api:8000";

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/`, { signal: AbortSignal.timeout(5000) });
    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      api_url: API_URL,
      api_response: data,
      status: response.status,
    });
  } catch (error: any) {
    return NextResponse.json({
      success: false,
      api_url: API_URL,
      error: error.message,
    }, { status: 500 });
  }
}

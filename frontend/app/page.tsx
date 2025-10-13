"use client"
import LandingNav from "@/components/navigation/landingNav";
import { useEffect } from "react";

export default function Home() {
  useEffect(() => {
    const fetchData = async () => {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

      if (!backendUrl) {
        console.warn("NEXT_PUBLIC_BACKEND_URL is not set");
        return;
      }

      const apiUrl = backendUrl.endsWith("/") ? backendUrl : `${backendUrl}/`;
      const response = await fetch(apiUrl);
      console.log(response);
      const data = await response.json();
      console.log(data);
    };
    fetchData();
  }, []);
  return (
    <>
    <LandingNav/>
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-4xl font-bold">Welcome to ThumbnailAI</h1>
      <p className="mt-4 text-lg">Your AI-powered thumbnail generator</p>
    </main>
    </>
    
  );
}
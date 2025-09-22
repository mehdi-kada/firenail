"use client"
import { useEffect } from "react";

export default function Home() {
  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch("http://localhost:8000/");
      console.log(response);
      const data = await response.json();
      console.log(data);
    };
    fetchData();
  }, []);
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-4xl font-bold">Welcome to ThumbnailAI</h1>
      <p className="mt-4 text-lg">Your AI-powered thumbnail generator</p>
    </main>
  );
}
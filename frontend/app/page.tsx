"use client"
import LandingNav from "@/components/navigation/landingNav";
import { useEffect } from "react";

export default function Home() {
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
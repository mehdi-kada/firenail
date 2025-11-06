"use client"
import LandingNav from "@/components/navigation/landingNav";
import { useEffect } from "react";
import Hero from "@/components/landingPage/Hero";
import { Feather } from "lucide-react";
import Features from "@/components/landingPage/Features";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-card">
      <LandingNav/>
      <main className="flex flex-col items-center justify-between">
        <Hero />
        <Features />
      </main>
    </div>
  );
}
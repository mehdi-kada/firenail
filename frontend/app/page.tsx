"use client"
import LandingNav from "@/components/navigation/landingNav";
import { useEffect } from "react";
import Hero from "@/components/landingPage/Hero";
import { Feather } from "lucide-react";
import Features from "@/components/landingPage/Features";

export default function Home() {
  return (
    <>
    <LandingNav/>
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <Hero />
      <Features />
    </main>
    </>
    
  );
}
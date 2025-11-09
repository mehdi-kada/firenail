"use client"
import LandingNav from "@/components/navigation/landingNav";
import { useEffect } from "react";
import Hero from "@/components/landingPage/Hero";
import { Feather } from "lucide-react";
import Features from "@/components/landingPage/Features";
import HowItWorks from "@/components/landingPage/HowItWorks";
import Pricing from "@/components/landingPage/Pricing";
import CTA from "@/components/landingPage/CTA";

export default function Home() {
  return (
    <div className="min-h-screen ">
      <LandingNav/>
      <main className="flex flex-col items-center gap-0 -mt-10">
        <Hero />
        <Features />
        <HowItWorks />
        <Pricing />
        <CTA />
      </main>
    </div>
  );
}
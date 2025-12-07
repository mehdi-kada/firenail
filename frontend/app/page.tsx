"use client"
import LandingNav from "@/components/navigation/landingNav";
import { useEffect } from "react";
import Hero from "@/components/landingPage/Hero";
import { Feather } from "lucide-react";
import Features from "@/components/landingPage/Features";
import HowItWorks from "@/components/landingPage/HowItWorks";
import Pricing from "@/components/landingPage/Pricing";
import CTA from "@/components/landingPage/CTA";
import Footer from "@/components/landingPage/Footer";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <LandingNav/>
      <main className="flex flex-col gap-0 flex-1 w-full">
        <Hero />
        <Features />
        <HowItWorks />
        <Pricing />
        <CTA />
      </main>
      <Footer />
    </div>
  );
}
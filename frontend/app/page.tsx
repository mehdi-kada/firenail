import type { Metadata } from "next";
import LandingNav from "@/components/navigation/landingNav";
import Hero from "@/components/landingPage/Hero";
import Features from "@/components/landingPage/Features";
import HowItWorks from "@/components/landingPage/HowItWorks";
import Pricing from "@/components/landingPage/Pricing";
import CTA from "@/components/landingPage/CTA";
import Footer from "@/components/landingPage/Footer";

export const metadata: Metadata = {
  title: "Firenail - AI YouTube Thumbnail Generator | Create Click-Worthy Thumbnails",
  description: "Transform any YouTube video URL into stunning, professional thumbnails with AI. Firenail analyzes your video content and generates eye-catching covers that boost clicks.",
  openGraph: {
    title: "Firenail - AI YouTube Thumbnail Generator",
    description: "Transform any YouTube video into stunning thumbnails with AI that understands your content.",
  },
};

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <LandingNav />
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
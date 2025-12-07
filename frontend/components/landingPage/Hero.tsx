"use client";

import { Button } from "@/components/ui/button";
import { ArrowRight, Play, Sparkles } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import BeforeAfterSlider from "./BeforeAfterSlider";

export default function Hero() {
  return (
    <section className="relative w-full pt-30 pb-20 lg:pt-18 lg:pb-32 overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[800px] bg-radial-[circle_at_center_top] from-primary/20 via-background to-background opacity-50 blur-3xl -z-10" />

      {/* Hero Collage Background */}
      <div className="absolute inset-0 w-full h-full -z-20 opacity-15 pointer-events-none select-none">
        <Image
          src="/hero-collage.png"
          alt="Creative Collage"
          fill
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/0 via-background/50 to-background" />
        <div className="absolute inset-0 bg-gradient-to-r from-background/50 via-transparent to-background/50" />
      </div>

      <div className="container mx-auto px-4 md:px-6 relative z-10">
        <div className="flex flex-col items-center text-center gap-8 max-w-5xl mx-auto">

          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm text-sm text-primary-foreground/80 hover:bg-white/10 transition-colors cursor-default"
          >
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="font-medium bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
              AI-Powered Thumbnail Generation
            </span>
          </motion.div>

          {/* Heading */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tight leading-[1.1]"
          >
            Viral Thumbnails <br className="hidden md:block" />
            <span className="bg-gradient-to-r from-primary via-orange-400 to-amber-500 bg-clip-text text-transparent">
              in Seconds.
            </span>
          </motion.h1>

          {/* Subheading */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg md:text-xl text-muted-foreground max-w-2xl leading-relaxed"
          >
            Stop wasting hours on design. Our AI analyzes your video content and generates high-CTR thumbnails instantly. Join 10,000+ creators growing faster.
          </motion.p>

          {/* Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center gap-4 mt-4"
          >
            <Link href="/generate">
              <Button size="lg" className="h-12 px-8 text-lg rounded-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_30px_-5px_var(--color-primary)] hover:shadow-[0_0_40px_-5px_var(--color-primary)] transition-all duration-300">
                Generate for Free
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
          </motion.div>
        </div>

        {/* Hero Image / Demo Area */}
        <motion.div
          initial={{ opacity: 0, y: 60, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.5, ease: "easeOut" }}
          className="mt-16 w-full max-w-5xl mx-auto"
        >
          <BeforeAfterSlider
            beforeImage="/before-thumbnail.png"
            afterImage="/after-thumbnail.png"
          />
        </motion.div>
      </div>
    </section>
  );
}
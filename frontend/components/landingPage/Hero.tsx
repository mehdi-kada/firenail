'use client';

import { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import AnimatedBackground from '@/components/ui/AnimatedBackground';
import { motion } from 'framer-motion';

export default function Hero() {
  const typedRef = useRef<HTMLSpanElement>(null);
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    // Typing animation effect
    if (typedRef.current) {
      const phrases = [
        'into Stunning Thumbnails',
        'Analyzed by AI',
        'to Professional Designs',
        'in 3 Minutes'
      ];
      let phraseIndex = 0;
      let charIndex = 0;
      let isDeleting = false;

      const type = () => {
        const currentPhrase = phrases[phraseIndex];

        if (!isDeleting && charIndex <= currentPhrase.length) {
          if (typedRef.current) {
            typedRef.current.textContent = currentPhrase.substring(0, charIndex);
          }
          charIndex++;
          setTimeout(type, 100);
        } else if (isDeleting && charIndex >= 0) {
          if (typedRef.current) {
            typedRef.current.textContent = currentPhrase.substring(0, charIndex);
          }
          charIndex--;
          setTimeout(type, 50);
        } else if (!isDeleting && charIndex > currentPhrase.length) {
          setTimeout(() => {
            isDeleting = true;
            type();
          }, 2000);
        } else if (isDeleting && charIndex < 0) {
          isDeleting = false;
          phraseIndex = (phraseIndex + 1) % phrases.length;
          setTimeout(type, 500);
        }
      };

      type();
    }
  }, []);

  const handleSliderMove = (e: React.MouseEvent<HTMLDivElement> | React.TouchEvent<HTMLDivElement>) => {
    if (!isDragging && e.type !== 'mousedown' && e.type !== 'touchstart') return;

    const container = e.currentTarget.getBoundingClientRect();
    let clientX: number;

    if ('touches' in e) {
      clientX = e.touches[0].clientX;
    } else {
      clientX = e.clientX;
    }

    const x = clientX - container.left;
    const percentage = (x / container.width) * 100;
    setSliderPosition(Math.min(Math.max(percentage, 0), 100));
  };

  return (
    <section className="relative min-h-screen w-full flex items-center overflow-hidden pt-20 lg:pt-0">
      {/* Content */}
      <div className="relative z-[2] w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Text Content */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="space-y-8"
            >
              <div className="space-y-4">
                <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
                  <span className="bg-gradient-to-r from-primary to-orange-600 bg-clip-text text-transparent">
                    YouTube URLs
                  </span>
                  <br />
                  <span ref={typedRef} className="text-foreground min-h-[1.2em] inline-block">
                    into Stunning Thumbnails
                  </span>
                  <span className="inline-block w-0.5 h-12 lg:h-16 bg-primary ml-1 animate-pulse align-middle" />
                </h1>
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4, duration: 0.8 }}
                  className="text-xl text-muted-foreground leading-relaxed"
                >
                  Firenail&apos;s AI analyzes your video&apos;s transcript, mines visual inspiration,
                  and generates on-brand thumbnails while you watch. No design skills required.
                </motion.p>
              </div>

              {/* CTA Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6, duration: 0.5 }}
                className="flex flex-col sm:flex-row gap-4"
              >
                <button className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-4 rounded-lg font-semibold text-lg transition-all hover:scale-105 hover:shadow-lg hover:shadow-primary/40">
                  Generate Your First Thumbnail
                </button>
                <button className="border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground px-8 py-4 rounded-lg font-semibold text-lg transition-all hover:scale-105">
                  View Demo
                </button>
              </motion.div>
            </motion.div>

            {/* Right Column - Before/After Slider */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
              className="relative space-y-4"
            >
              {/* Before/After Slider */}
              <div
                className="relative rounded-xl overflow-hidden shadow-2xl cursor-ew-resize select-none border-4 border-card/50"
                onMouseDown={(e) => {
                  setIsDragging(true);
                  handleSliderMove(e);
                }}
                onMouseMove={handleSliderMove}
                onMouseUp={() => setIsDragging(false)}
                onMouseLeave={() => setIsDragging(false)}
                onTouchStart={(e) => {
                  setIsDragging(true);
                  handleSliderMove(e);
                }}
                onTouchMove={handleSliderMove}
                onTouchEnd={() => setIsDragging(false)}
              >
                {/* Before Image (Background) */}
                <div className="relative w-full aspect-video">
                  <Image
                    src="/before-thumbnail-v2.png"
                    alt="Before - Manual Thumbnail Creation"
                    fill
                    className="object-cover"
                    priority
                  />
                  <div className="absolute top-4 right-4 bg-black/70 text-white px-3 py-1 rounded-md text-sm font-semibold backdrop-blur-sm">
                    BEFORE
                  </div>
                </div>

                {/* After Image (Overlay with clip) */}
                <div
                  className="absolute inset-0"
                  style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
                >
                  <Image
                    src="/after-thumbnail-v2.png"
                    alt="After - AI Generated Thumbnail"
                    fill
                    className="object-cover"
                    priority
                  />
                  <div className="absolute top-4 left-4 bg-primary/90 text-white px-3 py-1 rounded-md text-sm font-semibold shadow-lg">
                    AFTER
                  </div>
                </div>

                {/* Slider Line */}
                <div
                  className="absolute inset-y-0 w-1 bg-white shadow-[0_0_15px_rgba(0,0,0,0.5)] z-10"
                  style={{ left: `${sliderPosition}%` }}
                >
                  {/* Slider Handle */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-6 h-6 text-primary">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 15L12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Title Placeholder */}
              <div className="text-center">
                <h3 className="text-2xl font-bold text-foreground">
                  Transform Your Content in Seconds
                </h3>
                <p className="text-muted-foreground mt-2">
                  Drag the slider to see the difference
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Animated Background - Full hero section */}
      <div className="absolute inset-0 z-[1]">
        <AnimatedBackground />
      </div>
    </section>
  );
}
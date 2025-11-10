'use client';

import { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import AnimatedBackground from '@/components/ui/AnimatedBackground';

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
    <section className="relative min-h-screen flex items-center overflow-hidden">
      {/* Content */}
      <div className="relative z-[2] w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Text Content */}
            <div className="space-y-8">
              <div className="space-y-4">
                <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
                  <span className="bg-gradient-to-r from-primary to-orange-600 bg-clip-text text-transparent">
                    YouTube URLs
                  </span>
                  <br />
                  <span ref={typedRef} className="text-foreground">
                    into Stunning Thumbnails
                  </span>
                  <span className="inline-block w-0.5 h-12 lg:h-16 bg-primary ml-1 animate-pulse" />
                </h1>
                <p className="text-xl text-muted-foreground leading-relaxed">
                  Firenail&apos;s AI analyzes your video&apos;s transcript, mines visual inspiration, 
                  and generates on-brand thumbnails while you watch. No design skills required.
                </p>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                <button className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-4 rounded-lg font-semibold text-lg transition-all hover:scale-105 hover:shadow-lg hover:shadow-primary/40">
                  Generate Your First Thumbnail
                </button>
                <button className="border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground px-8 py-4 rounded-lg font-semibold text-lg transition-all hover:scale-105">
                  View Demo
                </button>
              </div>


            </div>

            {/* Right Column - Before/After Slider */}
            <div className="relative space-y-4">
              {/* Before/After Slider */}
              <div 
                className="relative rounded-lg overflow-hidden shadow-2xl cursor-ew-resize select-none"
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
                    src="/public/before-thumbnail.png"
                    alt="Before - Manual Thumbnail Creation"
                    fill
                    className="object-cover"
                    priority
                  />
                  <div className="absolute top-4 left-4 bg-black/70 text-white px-3 py-1 rounded-md text-sm font-semibold">
                    BEFORE
                  </div>
                </div>

                {/* After Image (Overlay with clip) */}
                <div 
                  className="absolute inset-0"
                  style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
                >
                  <Image
                    src="/resources/after-thumbnail.png"
                    alt="After - AI Generated Thumbnail"
                    fill
                    className="object-cover"
                    priority
                  />
                  <div className="absolute top-4 right-4 bg-primary/90 text-white px-3 py-1 rounded-md text-sm font-semibold">
                    AFTER
                  </div>
                </div>

                {/* Slider Line */}
                <div 
                  className="absolute inset-y-0 w-1 bg-white shadow-lg"
                  style={{ left: `${sliderPosition}%` }}
                >
                  {/* Slider Handle */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 bg-white rounded-full shadow-xl flex items-center justify-center">
                    <div className="flex gap-1">
                      <div className="w-0.5 h-6 bg-gray-400"></div>
                      <div className="w-0.5 h-6 bg-gray-400"></div>
                    </div>
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
            </div>
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
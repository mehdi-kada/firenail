'use client';

import { useState } from 'react';
import { Link as LinkIcon } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';


export default function CTA() {
  const [videoUrl, setVideoUrl] = useState('');
  const router = useRouter()

  const handleGenerate = () => {
    const encodedUrl = encodeURIComponent(videoUrl.trim());
    router.push(`/generate?videoUrl=${encodedUrl}`);

  };

  return (
    <section className="py-16 sm:py-24 px-4">
      <div className="max-w-7xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="flex flex-col items-center gap-8 rounded-xl bg-gradient-to-br from-card/80 to-card/40 border border-border backdrop-blur-sm px-6 py-12 sm:px-10 sm:py-16 shadow-2xl"
        >
          {/* Heading */}
          <div className="flex flex-col gap-3 text-center">
            <h2 className="text-3xl font-bold leading-tight tracking-tight text-foreground sm:text-4xl lg:text-5xl">
              Ready to Transform Your Thumbnails?
            </h2>
            <p className="max-w-2xl text-base sm:text-lg text-muted-foreground">
              Join thousands of creators who are saving time and getting more views.
              Paste your YouTube video link and watch the magic happen.
            </p>
          </div>

          {/* URL Input */}
          <div className="w-full max-w-2xl">
            <label className="flex flex-col gap-2">
              <span className="text-sm font-medium text-muted-foreground px-1">
                YouTube Video URL
              </span>
              <div className="flex w-full items-stretch rounded-xl overflow-hidden border border-border bg-background/50 focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition-all">
                {/* Icon */}
                <div className="hidden sm:flex items-center justify-center px-4 bg-muted/50 text-muted-foreground">
                  <LinkIcon className="w-5 h-5" />
                </div>

                {/* Input */}
                <input
                  type="url"
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="flex-1 px-4 py-4 bg-transparent text-foreground placeholder:text-muted-foreground/50 focus:outline-none text-sm sm:text-base"
                />

                {/* Button */}
                <div className="flex items-center pr-2 py-2">
                  <button
                    onClick={handleGenerate}
                    disabled={!videoUrl.trim()}
                    className="bg-primary hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed text-primary-foreground px-6 py-2.5 rounded-lg font-semibold text-sm sm:text-base transition-all hover:scale-105 hover:shadow-lg hover:shadow-primary/40 disabled:hover:scale-100 disabled:hover:shadow-none whitespace-nowrap"
                  >
                    Generate
                  </button>
                </div>
              </div>
            </label>
          </div>

          {/* Trust Indicators */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="flex flex-col sm:flex-row items-center gap-6 text-sm text-muted-foreground"
          >
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Free to try</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>No credit card required</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Instant results</span>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

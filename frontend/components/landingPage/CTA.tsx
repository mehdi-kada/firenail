"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import Link from "next/link";

export default function CTA() {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="container mx-auto px-4 md:px-6 relative">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="relative rounded-3xl overflow-hidden bg-primary px-6 py-20 text-center md:px-20 lg:py-28"
        >
          {/* Background Patterns */}
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 mix-blend-overlay"></div>
          <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-[600px] h-[600px] bg-white/10 rounded-full blur-[100px] pointer-events-none" />
          <div className="absolute bottom-0 left-0 translate-y-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-black/10 rounded-full blur-[100px] pointer-events-none" />

          <div className="relative z-10 max-w-3xl mx-auto">
            <h2 className="text-3xl md:text-5xl font-black text-white mb-6 tracking-tight">
              Ready to Skyrocket Your Views?
            </h2>
            <p className="text-lg md:text-xl text-white/90 mb-10 max-w-2xl mx-auto leading-relaxed">
              Join thousands of creators who are saving time and growing their channels with AI-generated thumbnails.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link href="/generate">
                <Button size="lg" className="h-14 px-8 text-lg rounded-full bg-white text-primary hover:bg-white/90 shadow-2xl border-none">
                  Start Generating Now
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
            <p className="mt-6 text-sm text-white/60">No credit card required for free trial.</p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

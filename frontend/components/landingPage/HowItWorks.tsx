"use client";

import { motion } from "framer-motion";
import { Link, Wand2, Download, ArrowRight } from "lucide-react";

const steps = [
  {
    number: "01",
    title: "Paste YouTube Link",
    description: "Simply paste the URL of your YouTube video. We'll automatically fetch the transcript and analyze the content.",
    icon: Link,
  },
  {
    number: "02",
    title: "AI Generation",
    description: "Our engine analyzes the context and generates a high-conversion thumbnail instantly.",
    icon: Wand2,
  },
  {
    number: "03",
    title: "Download & Publish",
    description: "Download your high-res image directly, or regenerate it with custom feedback to get it perfect.",
    icon: Download,
  },
];

export default function HowItWorks() {
  return (
    <section className="py-24 bg-card/30 relative border-y border-white/5">
      <div className="container mx-auto px-4 md:px-6">
        <div className="mb-16 md:text-center max-w-3xl mx-auto">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl md:text-5xl font-bold mb-6"
          >
            From idea to image in <span className="text-primary italic">seconds</span>
          </motion.h2>
        </div>

        <div className="relative grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
          {/* Connecting Line (Desktop) */}
          <div className="hidden md:block absolute top-12 left-[16%] right-[16%] h-[2px] bg-gradient-to-r from-transparent via-primary/30 to-transparent" />

          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.2 }}
              className="relative flex flex-col items-center text-center"
            >
              <div className="w-24 h-24 rounded-full bg-card border-4 border-background shadow-xl flex items-center justify-center mb-8 relative z-10 group">
                <step.icon className="w-10 h-10 text-primary group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold border-4 border-background">
                  {index + 1}
                </div>
              </div>

              <h3 className="text-2xl font-bold mb-4">{step.title}</h3>
              <p className="text-muted-foreground leading-relaxed max-w-sm">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

"use client";

import { motion } from "framer-motion";
import { Zap, Layout, Image as ImageIcon, Gauge, Wand2, TrendingUp } from "lucide-react";

const features = [
  {
    icon: Wand2,
    title: "AI-Powered Magic",
    description: "Our advanced algorithms analyze your video content to generate contextual, high-impact visuals immediately.",
  },
  {
    icon: TrendingUp,
    title: "CTR Optimization",
    description: "Every thumbnail is engineered to stop the scroll. Proven patterns that drive higher click-through rates.",
  },
  {
    icon: Gauge,
    title: "Lightning Fast",
    description: "Get professional results in seconds, not hours. Focus on creating content, not resizing fonts in Photoshop.",
  },
  {
    icon: Layout,
    title: "Smart Layouts",
    description: "Automatically arranges text and subjects for maximum readability on mobile and desktop screens.",
  },
  {
    icon: ImageIcon,
    title: "High-Res Exports",
    description: "Download crystal clear, YouTube-ready images in 1080p, perfectly optimized for upload.",
  },
  {
    icon: Zap,
    title: "Iterative Refinement",
    description: "Not happy with the result? Regenerate your thumbnail with custom instructions to perfection.",
  },
];

export default function Features() {
  return (
    <section className="py-24 relative overflow-hidden bg-background">
      {/* Decorative background blobs */}
      <div className="absolute top-1/4 -right-64 w-96 h-96 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -left-64 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="container mx-auto px-4 md:px-6 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl md:text-5xl font-bold mb-6 tracking-tight"
          >
            Everything you need to <span className="text-primary">go viral</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-lg text-muted-foreground"
          >
            Powerful features designed for modern creators. We handle the design science, you handle the content.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="group p-8 rounded-2xl bg-card border border-white/5 hover:border-primary/20 hover:bg-white/[0.02] transition-colors duration-300"
            >
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <feature.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
              <p className="text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

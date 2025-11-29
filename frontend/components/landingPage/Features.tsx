'use client';

import AnimatedBackground from '@/components/ui/AnimatedBackground';
import { motion } from 'framer-motion';

export default function Features() {
  const features = [
    {
      icon: "tips_and_updates",
      title: "AI-Powered Suggestions",
      description:
        "Our AI analyzes your video content, title, and description to generate thumbnails with the highest click-through potential.",
    },
    {
      icon: "palette",
      title: "Brand Consistency",
      description:
        "Upload your brand's colors, fonts, and logos to ensure every thumbnail is perfectly on-brand.",
    },
    {
      icon: "trending_up",
      title: "High-Click-Through-Rate Designs",
      description:
        "We use data from millions of high-performing videos to create designs that are proven to get clicks.",
    },
    {
      icon: "photo_library",
      title: "Unlimited Variations",
      description:
        "Generate endless thumbnail options for any video. A/B test different styles to see what your audience loves.",
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <section className="relative py-16 sm:py-24 space-y-12 overflow-hidden">
      {/* Animated Background - Only upper portion with fade */}
      <div className="absolute top-0 left-0 right-0 h-1/3 z-[1]">
        <AnimatedBackground fadeInTop={true} />
      </div>

      {/* Content */}
      <div className="relative z-[2]">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center px-4"
        >
          <h2 className="text-foreground text-3xl sm:text-4xl font-bold leading-tight tracking-tight">
            Features That Drive Clicks
          </h2>
          <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
            Everything you need to create thumbnails that not only look good, but
            perform even better.
          </p>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 gap-8 px-4 mt-12"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="p-6 bg-card rounded-lg border border-border transition-all duration-300 hover:border-primary hover:shadow-lg hover:shadow-primary/20 cursor-pointer"
            >
              <span className="material-symbols-outlined text-primary !text-3xl mb-3">
                {feature.icon}
              </span>
              <h3 className="text-xl font-bold mb-2 text-foreground">
                {feature.title}
              </h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

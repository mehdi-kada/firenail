'use client';

import AnimatedBackground from '@/components/ui/AnimatedBackground';

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

  return (
    <section className="relative py-16 sm:py-24 space-y-12 overflow-hidden">
      {/* Animated Background - Only upper portion with fade */}
      <div className="absolute top-0 left-0 right-0 h-1/3 z-[1]">
        <AnimatedBackground fadeInTop={true} />
      </div>

      {/* Content */}
      <div className="relative z-[2]">
        {/* Section Header */}
        <div className="text-center px-4">
        <h2 className="text-foreground text-3xl sm:text-4xl font-bold leading-tight tracking-tight">
          Features That Drive Clicks
        </h2>
        <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
          Everything you need to create thumbnails that not only look good, but
          perform even better.
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 px-4">
        {features.map((feature, index) => (
          <div
            key={index}
            className="p-6 bg-card rounded-lg border border-border"
          >
            <span className="material-symbols-outlined text-primary !text-3xl mb-3">
              {feature.icon}
            </span>
            <h3 className="text-xl font-bold mb-2 text-foreground">
              {feature.title}
            </h3>
            <p className="text-muted-foreground">{feature.description}</p>
          </div>
        ))}
      </div>
      </div>
    </section>
  );
}

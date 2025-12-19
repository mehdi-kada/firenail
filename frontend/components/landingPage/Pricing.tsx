"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";

const plans = [
  {
    name: "Basic",
    price: "Free",
    suffix: "",
    description: "For individuals getting started.",
    features: ["Up to 5 video transcripts per month", "Up to 10 image generations", "Community support"],
    featured: false,
  },
  {
    name: "Pro",
    price: "$12.99",
    suffix: "/month",
    description: "For power users and small teams.",
    features: ["Unlimited video transcripts", "Unlimited image generations", "Priority email support", "Advanced generation options"],
    featured: true,
  },
  {
    name: "Pro",
    price: "$99.99",
    suffix: "/year",
    description: "Best value - Save 35% annually!",
    features: ["Unlimited video transcripts", "Unlimited image generations", "Priority email support", "Advanced generation options", "2 months free!"],
    featured: false,
  },
];

export default function Pricing() {
  return (
    <section className="py-32 relative overflow-hidden" id="pricing">
      <div className="container mx-auto px-4 md:px-6 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-4xl md:text-5xl font-bold mb-6"
          >
            Simple, Transparent Pricing
          </motion.h2>
          <p className="text-lg text-muted-foreground">
            Choose the plan that fits your creation workflow. Cancel anytime.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto items-center">
          {plans.map((plan, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className={`relative p-8 rounded-3xl border ${plan.featured
                ? "bg-gradient-to-b from-card to-background border-primary/50 shadow-[0_0_40px_-10px_rgba(255,85,0,0.3)] z-10 scale-105"
                : "bg-card/40 border-white/5 hover:border-white/10"
                } flex flex-col h-full`}
            >
              {plan.featured && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                  Most Popular
                </div>
              )}

              <div className="mb-8">
                <h3 className="text-xl font-bold mb-2 text-foreground">{plan.name}</h3>
                <p className="text-sm text-muted-foreground mb-6">{plan.description}</p>
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-muted-foreground">{plan.suffix}</span>
                </div>
              </div>

              <ul className="flex-1 space-y-4 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-3 text-sm text-muted-foreground">
                    <Check className={`w-5 h-5 ${plan.featured ? "text-primary" : "text-gray-500"}`} />
                    {feature}
                  </li>
                ))}
              </ul>

              <Button
                variant={plan.featured ? "default" : "outline"}
                className={`w-full rounded-xl h-12 ${plan.featured
                  ? "bg-primary hover:bg-primary/90"
                  : "border-white/10 hover:bg-white/5 hover:text-white"
                  }`}
              >
                {plan.price === "0" ? "Start Free" : "Get Started"}
              </Button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

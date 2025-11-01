import { PricingPlan } from "@/components/pricing/PricingGrid"

interface GetPricingPlansParams {
  isPremium: boolean
  subscription?: {
    status: string
    plan_name: string
    current_period_end: string
    renews_at?: string | null
    cancel_at_period_end: boolean
  } | null
}

export function getPricingPlans({ isPremium, subscription }: GetPricingPlansParams): PricingPlan[] {
  return [
    {
      id: "basic",
      title: "Basic",
      price: "Free",
      description: "For individuals getting started.",
      ctaLabel: "Get Started",
      features: [
        "Up to 5 video transcripts per month",
        "Up to 10 image generations",
        "Community support",
      ],
      disabled: isPremium,
    },
    {
      id: "pro",
      title: "Pro",
      price: "$12.99",
      priceSuffix: "/month",
      description: "For power users and small teams.",
      ctaLabel: isPremium ? "Manage Subscription" : "Choose Plan",
      features: [
        "Unlimited video transcripts",
        "Unlimited image generations",
        "Priority email support",
        "Advanced generation options",
      ],
      highlighted: true,
      accentLabel: isPremium 
        ? (subscription?.status === "active" ? "✓ Active" : "⚠ Cancelled")
        : "Most Popular",
      productId: process.env.NEXT_PUBLIC_POLAR_MONTHLY_PRODUCT_ID,
    },
    {
      id: "yearly",
      title: "Pro",
      price: "$99.99",
      priceSuffix: "/year",
      description: "Best value - Save 35% annually!",
      ctaLabel: isPremium ? "Manage Subscription" : "Choose Yearly Plan",
      features: [
        "Unlimited video transcripts",
        "Unlimited image generations",
        "Priority email support",
        "Advanced generation options",
        "2 months free!",
      ],
      highlighted: false,
      accentLabel: isPremium 
        ? (subscription?.plan_name.includes("Yearly") || subscription?.plan_name.includes("year") ? "✓ Active" : undefined)
        : "Best Value",
      productId: process.env.NEXT_PUBLIC_POLAR_YEARLY_PRODUCT_ID,
    },
  ]
}

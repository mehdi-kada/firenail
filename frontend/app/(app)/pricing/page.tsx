import { PricingFooter } from "@/components/pricing/PricingFooter"
import { PricingGrid, type PricingPlan } from "@/components/pricing/PricingGrid"
import { PricingHero } from "@/components/pricing/PricingHero"

const plans: PricingPlan[] = [
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
  },
  {
    id: "pro",
    title: "Pro",
    price: "$19",
    priceSuffix: "/month",
    description: "For power users and small teams.",
    ctaLabel: "Choose Plan",
    features: [
      "Unlimited video transcripts",
      "Unlimited image generations",
      "Priority email support",
      "Advanced generation options",
    ],
    highlighted: true,
    accentLabel: "Most Popular",
  },
  {
    id: "enterprise",
    title: "Enterprise",
    price: "Contact Us",
    description: "For large organizations.",
    ctaLabel: "Contact Sales",
    features: [
      "Custom solutions & integrations",
      "Dedicated account manager",
      "Premium support & SLA",
    ],
  },
]

export default function PricingPage() {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16 sm:px-6 lg:px-8">
          <PricingHero
            title="Choose the plan that's right for you"
            description="Simple, transparent pricing. No hidden fees."
          />

          <PricingGrid plans={plans} />
        </div>
      </main>

      <PricingFooter />
    </div>
  )
}

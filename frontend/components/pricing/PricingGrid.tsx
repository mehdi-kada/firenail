import { PricingCard, type PricingCardProps } from "./PricingCard"

export type PricingPlan = PricingCardProps

type PricingGridProps = {
  plans: PricingPlan[]
}

export function PricingGrid({ plans }: PricingGridProps) {
  return (
    <div className="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
      {plans.map((plan) => (
        <PricingCard key={plan.id} {...plan} />
      ))}
    </div>
  )
}

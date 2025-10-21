import { PricingCard, type PricingCardProps } from "./PricingCard"

export type PricingPlan = PricingCardProps & {
  productId?: string
}

type PricingGridProps = {
  plans: PricingPlan[]
  onPlanClick?: (planId: string, productId?: string) => void
  loadingPlanId?: string | null
}

export function PricingGrid({ plans, onPlanClick, loadingPlanId }: PricingGridProps) {
  return (
    <div className="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
      {plans.map((plan) => (
        <PricingCard 
          key={plan.id} 
          {...plan}
          onCTAClick={() => onPlanClick?.(plan.id, plan.productId)}
          isLoading={loadingPlanId === plan.id}
        />
      ))}
    </div>
  )
}

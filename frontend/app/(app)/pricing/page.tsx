"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { PricingFooter } from "@/components/pricing/PricingFooter"
import { PricingGrid, type PricingPlan } from "@/components/pricing/PricingGrid"
import { PricingHero } from "@/components/pricing/PricingHero"
import { SubscriptionStatus } from "@/components/subscription/SubscriptionStatus"
import { useSubscription } from "@/hooks/useSubscription"
import { subscriptionApi } from "@/lib/api/subscriptions"
import { getPricingPlans } from "@/lib/constants/pricing"

export default function PricingPage() {
  const router = useRouter()
  const { subscription, isPremium, loading: subLoading } = useSubscription()
  const [loadingPlanId, setLoadingPlanId] = useState<string | null>(null)

  const handlePlanClick = async (planId: string, productId?: string) => {
    if (planId === "basic") {
      return
    }

    if (isPremium) {
      try {
        setLoadingPlanId(planId)
        const portalUrl = await subscriptionApi.getCustomerPortal()
        window.location.href = portalUrl
      } catch (error) {
        
        alert("Failed to open customer portal. Please try again.")
      } finally {
        setLoadingPlanId(null)
      }
      return
    }

    if (!productId) {
      alert("Product ID not configured")
      return
    }

    try {
      setLoadingPlanId(planId)
      const checkoutUrl = await subscriptionApi.createCheckout(productId)
      window.location.href = checkoutUrl
    } catch (error: any) {
      
      if (error.response?.status === 400) {
        alert("You already have an active subscription")
      } else {
        alert("Failed to start checkout. Please try again.")
      }
    } finally {
      setLoadingPlanId(null)
    }
  }

  const plans = getPricingPlans({ isPremium, subscription })

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16 sm:px-6 lg:px-8">
          <PricingHero
            title="Choose the plan that's right for you"
            description="Simple, transparent pricing. No hidden fees."
          />

          <SubscriptionStatus />

          <PricingGrid 
            plans={plans}
            onPlanClick={handlePlanClick}
            loadingPlanId={loadingPlanId}
          />
        </div>
      </main>

      <PricingFooter />
    </div>
  )
}

"use client"

import { useSubscription } from "@/hooks/useSubscription"
import { Button } from "@/components/ui/button"
import { subscriptionApi } from "@/lib/api/subscriptions"
import { useState } from "react"

export function SubscriptionBanner() {
  const { subscription, isPremium } = useSubscription()
  const [loading, setLoading] = useState(false)

  if (!isPremium) return null

  const handleManage = async () => {
    try {
      setLoading(true)
      const portalUrl = await subscriptionApi.getCustomerPortal()
      window.location.href = portalUrl
    } catch (error) {
      alert("Failed to open customer portal")
    } finally {
      setLoading(false)
    }
  }

  const isExpiring = subscription?.cancel_at_period_end

  return (
    <div className={`border-b px-4 py-2 ${isExpiring ? 'bg-orange-500/10 border-orange-500/20' : 'bg-primary/10 border-primary/20'}`}>
      <div className="container mx-auto flex items-center justify-between text-sm">
        <p>
          {subscription?.status === "active" && !isExpiring
            ? `✓ Premium active - Renews ${new Date(subscription.renews_at || subscription.current_period_end).toLocaleDateString()}`
            : `⚠ Subscription ends ${new Date(subscription?.current_period_end || "").toLocaleDateString()}`
          }
        </p>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleManage}
          disabled={loading}
        >
          {loading ? "Loading..." : "Manage"}
        </Button>
      </div>
    </div>
  )
}

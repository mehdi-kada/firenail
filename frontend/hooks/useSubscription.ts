"use client"

import { useEffect, useState } from "react"
import { subscriptionApi } from "@/lib/api/subscriptions"
import type { Subscription } from "@/lib/types/subscription"
import { createClient } from "@/lib/supabase/client"

export function useSubscription() {
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Check if user has premium access (includes grace period for cancelled subs)
  const isPremium = subscription?.status === "active" || 
    (subscription?.status === "cancelled" && 
     new Date(subscription.current_period_end) > new Date())

  const fetchSubscription = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await subscriptionApi.getUserSubscription()
      setSubscription(data)
    } catch (err: any) {
      setError(err.message || "Failed to fetch subscription")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const supabase = createClient()
    
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        fetchSubscription()
      } else {
        setLoading(false)
      }
    })
  }, [])

  return {
    subscription,
    isPremium,
    loading,
    error,
    refetch: fetchSubscription,
  }
}

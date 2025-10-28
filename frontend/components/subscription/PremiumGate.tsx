"use client"

import { useSubscription } from "@/hooks/useSubscription"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"

type PremiumGateProps = {
  children: React.ReactNode
  fallback?: React.ReactNode
  feature?: string
}

export function PremiumGate({ children, fallback, feature = "this feature" }: PremiumGateProps) {
  const { isPremium, loading } = useSubscription()
  const router = useRouter()

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    )
  }

  if (!isPremium) {
    return fallback || (
      <div className="text-center p-12 border-2 border-dashed border-border rounded-lg bg-card">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6 text-primary"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
        </div>
        <h3 className="text-xl font-semibold mb-2">Premium Feature</h3>
        <p className="text-muted-foreground mb-6">
          Upgrade to Pro to access {feature}
        </p>
        <Button onClick={() => router.push("/pricing")} size="lg">
          Upgrade to Pro
        </Button>
      </div>
    )
  }

  return <>{children}</>
}

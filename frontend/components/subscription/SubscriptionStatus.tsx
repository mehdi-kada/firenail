"use client"

import { useSubscription } from "@/hooks/useSubscription"
import { subscriptionApi } from "@/lib/api/subscriptions"
import { useState } from "react"

export function SubscriptionStatus() {
  const { subscription, isPremium } = useSubscription()
  const [loading, setLoading] = useState(false)

  if (!isPremium || !subscription) return null

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
  const renewalDate = new Date(subscription.renews_at || subscription.current_period_end).toLocaleDateString()

  return (
    <div className="max-w-4xl mx-auto mb-12">
      <div className="group relative bg-secondary-background border border-border rounded-lg p-5 flex items-center justify-between overflow-hidden transition-all duration-300 hover:border-primary/80 hover:shadow-lg hover:shadow-primary/10">
        {/* Animated glow background */}
        <div className="absolute -left-1 -top-1 w-1/4 h-1/4 bg-primary/20 blur-3xl animate-glow"></div>
        
        <div className="flex items-center gap-4 relative z-10">
          {/* Checkmark icon */}
          <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center border-2 border-primary/30">
            <svg 
              className="w-7 h-7 text-primary animate-check-grow" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2.5" 
              viewBox="0 0 24 24" 
              xmlns="http://www.w3.org/2000/svg"
            >
              <path 
                d="M5 13l4 4L19 7" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              />
            </svg>
          </div>
          
          <div>
            <h3 className="font-bold text-lg text-text">
              {isExpiring ? "Subscription Ending" : `${subscription.plan_name} Active`}
            </h3>
            <p className="text-sm text-text/70">
              {isExpiring 
                ? `Your plan expires on ${renewalDate}.`
                : `Your plan renews on ${renewalDate}.`
              }
            </p>
          </div>
        </div>
        
        <button
          onClick={handleManage}
          disabled={loading}
          className="px-5 py-2.5 bg-background border border-border rounded-full text-sm font-medium hover:bg-primary hover:text-white hover:border-primary transition-all duration-300 group-hover:border-primary disabled:opacity-50 disabled:cursor-not-allowed relative z-10"
        >
          {loading ? "Loading..." : "Manage"}
        </button>
      </div>
      
      <style jsx>{`
        @keyframes check-grow {
          0% { transform: scale(0); }
          80% { transform: scale(1.2); }
          100% { transform: scale(1); }
        }
        
        @keyframes glow {
          0%, 100% { box-shadow: 0 0 5px -2px hsl(var(--primary)), 0 0 10px -2px hsl(var(--primary)); }
          50% { box-shadow: 0 0 10px 0px hsl(var(--primary)), 0 0 20px 0px hsl(var(--primary)); }
        }
        
        .animate-check-grow {
          animation: check-grow 0.5s ease-out forwards;
        }
        
        .animate-glow {
          animation: glow 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  )
}

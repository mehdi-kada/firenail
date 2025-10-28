export type SubscriptionStatus = "active" | "cancelled" | "expired" | "on_trial" | "paused" | "unpaid"

export interface Subscription {
  id: string
  user_id: string
  polar_subscription_id: string
  polar_customer_id: string
  status: SubscriptionStatus
  plan_name: string
  current_period_start: string
  current_period_end: string
  cancel_at_period_end: boolean
  renews_at: string | null
  created_at: string
  updated_at: string
}

export interface CheckoutResponse {
  checkout_url: string
}

export interface CustomerPortalResponse {
  portal_url: string
}

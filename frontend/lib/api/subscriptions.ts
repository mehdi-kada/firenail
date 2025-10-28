import api from "@/lib/axios/axios"
import type { Subscription, CheckoutResponse, CustomerPortalResponse } from "@/lib/types/subscription"

export const subscriptionApi = {
  // Get current user's subscription
  getUserSubscription: async (): Promise<Subscription | null> => {
    try {
      const { data } = await api.get<Subscription>("/api/subscription/status")
      return data
    } catch (error: any) {
      if (error.response?.status === 404) return null
      throw error
    }
  },

  // Create checkout session (calls FastAPI backend)
  createCheckout: async (productId: string): Promise<string> => {
    const { data } = await api.post<CheckoutResponse>(
      "/api/subscription/create-checkout",
      { product_id: productId }
    )
    return data.checkout_url
  },

  // Get customer portal URL (calls FastAPI backend)
  getCustomerPortal: async (): Promise<string> => {
    const { data } = await api.get<CustomerPortalResponse>("/api/customer-portal")
    return data.portal_url
  },
}

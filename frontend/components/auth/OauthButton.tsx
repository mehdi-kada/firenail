'use client'

import { cn } from '@/lib/utils'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { Loader2 } from 'lucide-react'
import { useState } from 'react'

export function OauthButton({ className, ...props }: React.ComponentPropsWithoutRef<'div'>) {
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSocialLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    const supabase = createClient()
    setIsLoading(true)
    setError(null)

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/oauth?next=/thumbnails`,
        },
      })

      if (error) throw error
    } catch (error: unknown) {
      setError(error instanceof Error ? error.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={cn('flex flex-col mt-5', className)} {...props}>
      <form onSubmit={handleSocialLogin} className="space-y-4">
        {error && (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}
        <Button
          type="submit"
          className="w-full bg-gradient-to-r from-primary via-primary/90 to-primary/80 text-primary-foreground transition-all hover:from-primary/95 hover:via-primary hover:to-primary/85 focus-visible:ring-primary/40"
          disabled={isLoading}
          aria-busy={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="size-5 animate-spin" aria-hidden="true" />
              Redirecting
                            
            </>
          ) : (
            <>
              <GoogleIcon className="size-5" aria-hidden="true" />
              Continue with Google
            </>
          )}
        </Button>
      </form>
    </div>
  )
}

function GoogleIcon({ className }: { className?: string }) {
  return (
    <svg
      className={cn('size-4 text-primary-foreground', className)}
      viewBox="0 0 24 24"
      role="img"
      aria-label="Google icon"
    >
      <path
        d="M21.35 11.1h-9.9v2.91h5.62c-.24 1.47-1.68 4.32-5.62 4.32-3.38 0-6.14-2.79-6.14-6.23s2.76-6.24 6.14-6.24c1.92 0 3.2.82 3.94 1.53l2.69-2.6C16.59 2.7 14.36 1.7 11.45 1.7 5.9 1.7 1.4 6.22 1.4 11.7s4.5 10 10.05 10c5.81 0 9.65-4.07 9.65-9.8 0-.66-.07-1.17-.15-1.8Z"
        fill="currentColor"
      />
    </svg>
  )
}
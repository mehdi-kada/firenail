'use client'

import { useState } from 'react'
import { isAxiosError } from 'axios'
import Link from 'next/link'

import { cn } from '@/lib/utils'
import api from '@/lib/axios/axios'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

type UrlInputFormProps = React.ComponentPropsWithoutRef<'form'> & {
  onTaskCreated?: (id: string) => void
  isGenerating?: boolean
}

const TASKS_ENDPOINT = '/api/tasks/'

type ErrorState = {
  message: string
  isLimitError?: boolean
}

export function UrlInputForm({ className, onTaskCreated, isGenerating = false, ...props }: UrlInputFormProps) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState<ErrorState | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const validateUrl = (value: string) => {
    if (!value.trim()) {
      return 'Please paste a YouTube URL to get started.'
    }

    // Basic URL validation
    try {
      const parsed = new URL(value.trim())
      if (!['http:', 'https:'].includes(parsed.protocol)) {
        return 'Only HTTP and HTTPS URLs are supported.'
      }
      
      const hostname = parsed.hostname.toLowerCase()
      const isYouTube = hostname === 'youtube.com' || 
                        hostname === 'www.youtube.com' || 
                        hostname === 'youtu.be' || 
                        hostname === 'www.youtu.be'
      
      if (!isYouTube) {
        return 'Please provide a valid YouTube URL (youtube.com or youtu.be).'
      }
      
      return null
    } catch (err) {
      return 'Please enter a valid YouTube URL.'
    }
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const validationError = validateUrl(url)
    if (validationError) {
      setError({ message: validationError })
      return
    }

    const normalizedUrl = url.trim()

    setIsSubmitting(true)
    setError(null)

    try {
      const response = await api.post(TASKS_ENDPOINT, { url: normalizedUrl })
      const data = response.data
      setUrl('')
      onTaskCreated?.(data.task_id)
    } catch (err: unknown) {
      if (isAxiosError(err)) {
        const errorData = err.response?.data
        
        if (errorData?.detail && Array.isArray(errorData.detail)) {
          const firstError = errorData.detail[0]
          if (firstError?.msg) {
            setError({ message: firstError.msg })
          } else {
            setError({ message: 'Invalid YouTube URL. Please check and try again.' })
          }
        } else if (errorData?.detail && typeof errorData.detail === 'object') {
          if (errorData.detail.error === 'Usage limit exceeded') {
            const { message, current, limit, plan } = errorData.detail
            setError({
              message: `${message || 'Usage limit exceeded'}. You've used ${current} of ${limit} images on the ${plan} plan. Please upgrade to continue.`,
              isLimitError: true
            })
          } else {
            setError({ message: errorData.detail.message || 'Unable to process your request. Please try again.' })
          }
        } else {
          const message = errorData?.message ?? errorData?.detail
          setError({ message: typeof message === 'string' ? message : 'Unable to process your request. Please try again.' })
        }
      } else {
        setError({ message: 'Something went wrong. Please try again.' })
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const isBusy = isSubmitting || isGenerating

  return (
    <form onSubmit={handleSubmit} className={cn('w-full max-w-2xl mx-auto', className)} {...props} noValidate>
      <div className="relative flex items-center">
        <Input
          className="w-full h-16 pl-8 pr-44 rounded-full bg-card/80 backdrop-blur-sm border-2 border-white/5 focus-visible:border-primary/50 focus-visible:ring-4 focus-visible:ring-primary/10 text-lg placeholder:text-muted-foreground/60 shadow-xl transition-all duration-300"
          placeholder="Paste your YouTube URL here..."
          type="url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          aria-invalid={Boolean(error)}
          autoComplete="url"
          required
        />
        
        <Button
          className="absolute right-2 h-12 px-8 rounded-full bg-primary text-primary-foreground font-bold text-base tracking-wide shadow-lg shadow-primary/20 active:scale-95 transition-all duration-200"
          type="submit"
          disabled={isBusy}
          aria-busy={isBusy}
        >
          {isBusy ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              <span className="opacity-80">Generating</span>
            </span>
          ) : (
            'Generate'
          )}
        </Button>
      </div>

      {error && (
        <div className="mt-6 p-4 rounded-2xl bg-destructive/10 border border-destructive/20 text-destructive text-center animate-in slide-in-from-top-2 fade-in duration-300 backdrop-blur-sm">
          <p className="font-medium flex items-center justify-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
            {error.message}
          </p>
          {error.isLimitError && (
            <Link href="/pricing" className="inline-flex items-center gap-1 mt-2 text-sm font-semibold hover:text-destructive/80 transition-colors group">
              Upgrade Plan 
              <span className="group-hover:translate-x-0.5 transition-transform">→</span>
            </Link>
          )}
        </div>
      )}
    </form>
  )
}

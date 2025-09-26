'use client'

import { useState } from 'react'
import { isAxiosError } from 'axios'

import { cn } from '@/lib/utils'
import api from '@/lib/axios/axios'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

type UrlInputFormProps = React.ComponentPropsWithoutRef<'form'>

const GENERATE_ENDPOINT = '/generate'

export function UrlInputForm({ className, ...props }: UrlInputFormProps) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const validateUrl = (value: string) => {
    if (!value.trim()) {
      return 'Please paste a URL before submitting.'
    }

    try {
      const parsed = new URL(value.trim())
      if (!['http:', 'https:'].includes(parsed.protocol)) {
        return 'Only HTTP and HTTPS URLs are supported.'
      }
      return null
    } catch (err) {
      return 'Make sure the link is a valid URL.'
    }
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const validationError = validateUrl(url)
    if (validationError) {
      setError(validationError)
      setStatus(null)
      return
    }

    const normalizedUrl = url.trim()

    setIsSubmitting(true)
    setError(null)
    setStatus(null)

    try {
      await api.post(GENERATE_ENDPOINT, { url: normalizedUrl })
      setStatus('Your link was sent. We\'ll start generating in the background.')
      setUrl('')
    } catch (err: unknown) {
      if (isAxiosError(err)) {
        const message = err.response?.data?.message ?? err.response?.data?.detail
        setError(message ?? 'We could not reach the generator. Please try again.')
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className={cn('', className)} {...props} noValidate>
      <div className="relative">
        <Input
          className="w-full h-14 pl-6 pr-36 rounded-full bg-secondary-background border border-border focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all"
          placeholder="Enter YouTube video URL"
          type="url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          aria-invalid={Boolean(error)}
          autoComplete="url"
          required
        />
        <Button
          className="absolute inset-y-2 right-1.5 px-8 py-2 bg-primary text-white text-sm font-bold rounded-full hover:bg-opacity-90 transition-all"
          type="submit"
          disabled={isSubmitting}
          aria-busy={isSubmitting}
        >
          {isSubmitting ? 'Submitting…' : 'Generate'}
        </Button>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {status && <p className="text-sm text-muted-foreground">{status}</p>}
    </form>
  )
}

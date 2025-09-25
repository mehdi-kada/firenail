'use client'

import { useState } from 'react'
import { isAxiosError } from 'axios'

import { cn } from '@/lib/utils'
import api from '@/lib/axios/axios'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'

type UrlInputFormProps = React.ComponentPropsWithoutRef<'div'>

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
    <Card className={cn('w-full max-w-xl', className)} {...props}>
      <CardHeader>
        <CardTitle>Generate thumbnails</CardTitle>
        <CardDescription>Drop in a video URL and we\'ll handle the rest.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
          <div className="grid gap-2">
            <Label htmlFor="source-url">Source URL</Label>
            <div className="flex flex-col gap-2 sm:flex-row">
              <Input
                id="source-url"
                type="url"
                placeholder="https://example.com/video"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                aria-invalid={Boolean(error)}
                autoComplete="url"
                required
              />
              <Button type="submit" className="sm:w-auto" disabled={isSubmitting} aria-busy={isSubmitting}>
                {isSubmitting ? 'Submitting…' : 'Generate'}
              </Button>
            </div>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          {status && <p className="text-sm text-muted-foreground">{status}</p>}
        </form>
      </CardContent>
    </Card>
  )
}

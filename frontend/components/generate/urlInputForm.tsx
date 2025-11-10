'use client'

import { useState } from 'react'
import { isAxiosError } from 'axios'

import { cn } from '@/lib/utils'
import api from '@/lib/axios/axios'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

type UrlInputFormProps = React.ComponentPropsWithoutRef<'form'> & {
  onTaskCreated?: (id: string) => void
  isGenerating?: boolean
}

const TASKS_ENDPOINT = '/api/tasks/'

export function UrlInputForm({ className, onTaskCreated, isGenerating = false, ...props }: UrlInputFormProps) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState<string | null>(null)
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
      setError(validationError)
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
            setError(firstError.msg)
          } else {
            setError('Invalid YouTube URL. Please check and try again.')
          }
        } else {
          const message = errorData?.message ?? errorData?.detail
          setError(message ?? 'Unable to process your request. Please try again.')
        }
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const isBusy = isSubmitting || isGenerating

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
          disabled={isBusy}
          aria-busy={isBusy}
        >
          {isBusy ? 'Generating...' : 'Generate'}
        </Button>
      </div>
      {error && <p className="mt-2 text-sm text-destructive">{error}</p>}
    </form>
  )
}

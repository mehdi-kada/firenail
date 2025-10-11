'use client'

import { useEffect, useState } from 'react'
import { isAxiosError } from 'axios'

import api from '@/lib/axios/axios'
import { ThumbnailCard } from '@/components/thumbnails/thumbnailCard'

type ThumbnailResponse = {
  id: string
  job_id: string
  storage_url: string
  keywords: string[]
  created_at: string
}

export default function ThumbnailsPage() {
  const [thumbnails, setThumbnails] = useState<ThumbnailResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchThumbnails = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const response = await api.get<ThumbnailResponse[]>('/api/thumbnails/')
        console.log("thumbnails are : ", response.data)
        setThumbnails(response.data)
      } catch (err: unknown) {
        if (isAxiosError(err)) {
          const message = err.response?.data?.detail || err.message
          setError(message || 'Could not load thumbnails. Please try again later.')
        } else {
          setError('Could not load thumbnails. Please try again later.')
        }
      } finally {
        setIsLoading(false)
      }
    }

    fetchThumbnails()
  }, [])

  return (
    <div className="container mx-auto min-h-screen px-4 py-12 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto text-center">
        <h1 className="text-4xl font-bold tracking-tight md:text-5xl">Your Generated Thumbnails</h1>
        <p className="text-text/80 mt-4 text-lg">
          Browse and manage all the thumbnails you&apos;ve created for your YouTube videos.
        </p>
      </div>

      <div className="mt-12">
        {isLoading ? (
          <p className="text-text/70 text-center text-sm">Loading your thumbnails…</p>
        ) : error ? (
          <p className="text-destructive text-center text-sm">{error}</p>
        ) : thumbnails.length === 0 ? (
          <div className="border-border bg-secondary-background mx-auto max-w-xl rounded-lg border p-8 text-center">
            <h2 className="text-text text-xl font-semibold">No thumbnails yet</h2>
            <p className="text-text/80 mt-2 text-sm">
              Once you generate a thumbnail, it will appear here for quick access and downloads.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {thumbnails.map((thumbnail) => (
              <ThumbnailCard
                key={thumbnail.id}
                storageUrl={thumbnail.storage_url}
                createdAt={thumbnail.created_at}
                keywords={thumbnail.keywords}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
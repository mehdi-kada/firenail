'use client'

import { useEffect, useState, useCallback } from 'react'
import { isAxiosError } from 'axios'

import api from '@/lib/axios/axios'
import { ThumbnailCard } from '@/components/thumbnails/thumbnailCard'
import { Pagination } from '@/components/ui/pagination'

type ThumbnailResponse = {
  id: string
  job_id: string
  storage_url: string[]
  video_title?: string | null
  keywords: string[]
  created_at: string
}

type PaginatedThumbnailResponse = {
  items: ThumbnailResponse[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export default function ThumbnailsPage() {
  const [thumbnails, setThumbnails] = useState<ThumbnailResponse[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchThumbnails = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const response = await api.get<PaginatedThumbnailResponse>('/api/thumbnails/', {
          params: {
            page: currentPage,
            page_size: 12,
          },
        })

        setThumbnails(response.data.items)
        setTotalPages(response.data.total_pages)
        setTotal(response.data.total)
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
  }, [currentPage])

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Optimized: Memoized callback to ensure ThumbnailCard props remain stable, preventing unnecessary re-renders.
  const handleRegenerate = useCallback((updatedThumbnail: ThumbnailResponse) => {
    setThumbnails((prev) =>
      prev.map((t) => (t.id === updatedThumbnail.id ? updatedThumbnail : t))
    )
  }, [])

  return (
    <div className="container mx-auto min-h-screen px-4 py-12 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto text-center">
        <h1 className="text-4xl font-bold tracking-tight md:text-5xl">Your Generated Thumbnails</h1>
        <p className="text-text/80 mt-4 text-lg">
          Browse and manage all the thumbnails you&apos;ve created for your YouTube videos.
        </p>
        {total > 0 && (
          <p className="text-text/60 mt-2 text-sm">
            Showing {thumbnails.length} of {total} thumbnails
          </p>
        )}
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
          <>
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {thumbnails.map((thumbnail, index) => (
                <ThumbnailCard
                  key={thumbnail.id}
                  id={thumbnail.id}
                  storageUrl={thumbnail.storage_url}
                  title={thumbnail.video_title}
                  createdAt={thumbnail.created_at}
                  keywords={thumbnail.keywords}
                  priority={index < 6}
                  onRegenerate={handleRegenerate}
                />
              ))}
            </div>

            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
              className="mt-12"
            />
          </>
        )}
      </div>
    </div>
  )
}
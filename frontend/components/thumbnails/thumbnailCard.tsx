'use client'

import * as React from 'react'
import Image from 'next/image'

import { Button } from '@/components/ui/button'

type ThumbnailCardProps = {
  storageUrl: string
  title?: string | null
  createdAt?: string | Date | null
  keywords?: string[] | null
  onDownload?: () => void
  secondaryHref?: string
  priority?: boolean
}

export function ThumbnailCard({
  storageUrl,
  title,
  createdAt,
  keywords,
  onDownload,
  secondaryHref,
  priority = false,
}: ThumbnailCardProps) {
  const [imageError, setImageError] = React.useState(false)

  const formattedDate = React.useMemo(() => {
    if (!createdAt) return null
    try {
      const date = typeof createdAt === 'string' ? new Date(createdAt) : createdAt
      return new Intl.DateTimeFormat('en', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }).format(date)
    } catch {
      return null
    }
  }, [createdAt])

  const keywordList = React.useMemo(() => (keywords ?? []).filter(Boolean), [keywords])

  const displayTitle = title || keywordList.join(', ') || 'Generated Thumbnail'

  const secondaryUrl = secondaryHref ?? storageUrl

  const handleImageError = () => {
    console.error('Image failed to load:', storageUrl)
    setImageError(true)
  }

  return (
    <div className="bg-secondary-background border-border flex flex-col rounded-lg border p-4">
      <div className="aspect-video w-full overflow-hidden rounded-md bg-background mb-4 relative">
        {storageUrl && !imageError ? (
          <Image
            src={storageUrl}
            alt={displayTitle}
            fill
            className="object-cover"
            onError={handleImageError}
            priority={priority}
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            placeholder="blur"
            blurDataURL="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNzAwIiBoZWlnaHQ9IjQ3NSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB2ZXJzaW9uPSIxLjEiLz4="
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-text/50 text-sm">
            {imageError ? 'Failed to load image' : 'No image available'}
          </div>
        )}
      </div>

      <div className="flex flex-col gap-3 flex-grow">
        <div>
          <h3 className="text-text text-lg font-bold">{displayTitle}</h3>
          {formattedDate ? (
            <p className="text-text/70 mt-1 text-sm">{formattedDate}</p>
          ) : null}
        </div>


      </div>

      <div className="mt-4 flex flex-col gap-2">
        <Button asChild onClick={onDownload} className="w-full bg-primary text-text font-bold hover:bg-opacity-90">
          <a href={storageUrl} download>
            Download Thumbnail
          </a>
        </Button>

        <Button
          asChild
          variant="outline"
          className="w-full border-primary/30 bg-primary/10 text-primary font-bold hover:bg-primary/20"
        >
          <a href={secondaryUrl} target="_blank" rel="noreferrer">
            Open in new tab
          </a>
        </Button>
      </div>
    </div>
  )
}

'use client'

import * as React from 'react'

import { Button } from '@/components/ui/button'

type ThumbnailCardProps = {
  storageUrl: string
  title?: string | null
  createdAt?: string | Date | null
  keywords?: string[] | null
  onDownload?: () => void
  secondaryHref?: string
}

export function ThumbnailCard({
  storageUrl,
  title,
  createdAt,
  keywords,
  onDownload,
  secondaryHref,
}: ThumbnailCardProps) {
  const [imageLoaded, setImageLoaded] = React.useState(false)
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

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    console.error('Image failed to load:', storageUrl)
    console.error('Error event:', e)
    setImageError(true)
  }

  const handleImageLoad = () => {
    setImageLoaded(true)
  }

  React.useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('ThumbnailCard received storageUrl:', storageUrl)
      console.log('storageUrl type:', typeof storageUrl, 'isEmpty:', !storageUrl)
    }
  }, [storageUrl])

  return (
    <div className="bg-secondary-background border-border flex flex-col rounded-lg border p-4">
      <div className="aspect-video w-full overflow-hidden rounded-md bg-background mb-4 relative">
        {storageUrl && !imageError ? (
          <>
            {!imageLoaded && (
              <div className="absolute inset-0 flex items-center justify-center bg-background">
                <div className="text-text/50 text-sm">Loading...</div>
              </div>
            )}
            <img
              src={storageUrl}
              alt={displayTitle}
              className="h-full w-full object-cover"
              loading="lazy"
              onError={handleImageError}
              onLoad={handleImageLoad}
              style={{ display: imageLoaded ? 'block' : 'none' }}
            />
          </>
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

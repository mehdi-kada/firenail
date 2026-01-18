'use client'

import { memo, useMemo, useState } from 'react'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { EditThumbnailDialog } from './EditThumbnailDialog'
import { ChevronLeft, ChevronRight } from 'lucide-react'

type ThumbnailCardProps = {
  id: string
  storageUrl: string[]
  title?: string | null
  createdAt?: string | Date | null
  keywords?: string[] | null
  onDownload?: () => void
  secondaryHref?: string
  priority?: boolean
  onRegenerate?: (newThumbnail: any) => void
}

/**
 * Optimized ThumbnailCard component.
 * Wrapped in React.memo to prevent unnecessary re-renders when parent state updates.
 * Ensure callbacks like onRegenerate are stable (useCallback) in the parent.
 */
function ThumbnailCardBase({
  id,
  storageUrl,
  title,
  createdAt,
  keywords,
  onDownload,
  secondaryHref,
  priority = false,
  onRegenerate,
}: ThumbnailCardProps) {
  const [imageError, setImageError] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)

  const imageList = useMemo(() => {
    return storageUrl || []
  }, [storageUrl])

  const currentImageUrl = imageList[currentIndex]

  const handleNext = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (currentIndex < imageList.length - 1) {
      setCurrentIndex((prev) => prev + 1)
    } else {
      setCurrentIndex(0) 
    }
  }

  const handlePrev = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1)
    } else {
      setCurrentIndex(imageList.length - 1)
    }
  }

  const formattedDate = useMemo(() => {
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

  const keywordList = useMemo(() => (keywords ?? []).filter(Boolean), [keywords])

  const displayTitle = title || keywordList.join(', ') || 'Generated Thumbnail'

  const secondaryUrl = secondaryHref ?? currentImageUrl

  const handleImageError = () => {
    setImageError(true)
  }

  const downloadImage = async () => {
    if (!currentImageUrl) return
    try {
      const response = await fetch(currentImageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `thumbnail-${id}-${currentIndex + 1}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      if (onDownload) onDownload();
    } catch (error) {
      console.error('Download failed:', error)
    }
  };

  return (
    <>
      <div className="bg-secondary-background border-border flex flex-col rounded-lg border p-4 transition-all duration-300 hover:shadow-lg hover:border-primary/50">
        <div className="aspect-video w-full overflow-hidden rounded-md bg-background mb-4 relative group">
          {currentImageUrl && !imageError ? (
            <>
              <Image
                src={currentImageUrl}
                alt={`${displayTitle} - Image ${currentIndex + 1}`}
                fill
                className="object-cover transition-transform duration-500 group-hover:scale-105"
                onError={handleImageError}
                priority={priority}
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                placeholder="blur"
                blurDataURL="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNzAwIiBoZWlnaHQ9IjQ3NSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB2ZXJzaW9uPSIxLjEiLz4="
              />

              {imageList.length > 1 && (
                <>
                  <div className="absolute inset-0 flex items-center justify-between p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 rounded-full bg-black/50 text-white hover:bg-black/70 backdrop-blur-sm"
                      onClick={handlePrev}
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 rounded-full bg-black/50 text-white hover:bg-black/70 backdrop-blur-sm"
                      onClick={handleNext}
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1.5">
                    {imageList.map((_, idx) => (
                      <div
                        key={idx}
                        className={`h-1.5 rounded-full transition-all duration-300 ${idx === currentIndex ? 'w-4 bg-primary' : 'w-1.5 bg-white/50'
                          }`}
                      />
                    ))}
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="flex h-full w-full items-center justify-center text-text/50 text-sm">
              {imageError ? 'Failed to load image' : 'No image available'}
            </div>
          )}
        </div>

        <div className="flex flex-col gap-3 flex-grow">
          <div>
            <h3 className="text-text text-lg font-bold line-clamp-1">{displayTitle}</h3>
            {formattedDate ? (
              <p className="text-text/70 mt-1 text-sm">{formattedDate}</p>
            ) : null}
          </div>
        </div>

        <div className="mt-4 flex flex-col gap-2">
          <div className="flex gap-2">
            <Button onClick={downloadImage} className="flex-1 bg-primary text-text font-bold hover:bg-opacity-90 transition-colors">
              Download
            </Button>
            {onRegenerate && (
              <Button
                onClick={() => setIsEditDialogOpen(true)}
                variant="outline"
                className="flex-1 border-primary/30 text-primary font-bold hover:bg-primary/10 transition-colors"
              >
                Edit
              </Button>
            )}
          </div>

          <Button
            asChild
            variant="outline"
            className="w-full border-primary/30 bg-primary/10 text-primary font-bold hover:bg-primary/20 transition-colors"
          >
            <a href={secondaryUrl} target="_blank" rel="noreferrer">
              Open in new tab
            </a>
          </Button>
        </div>
      </div>

      {onRegenerate && (
        <EditThumbnailDialog
          isOpen={isEditDialogOpen}
          onClose={() => setIsEditDialogOpen(false)}
          thumbnailId={id}
          imageUrl={currentImageUrl}
          onSuccess={(newThumbnail) => {
            onRegenerate(newThumbnail)
          }}
        />
      )}
    </>
  )
}

export const ThumbnailCard = memo(ThumbnailCardBase)
ThumbnailCard.displayName = 'ThumbnailCard'

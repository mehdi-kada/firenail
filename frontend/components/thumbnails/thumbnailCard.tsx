'use client'

import * as React from 'react'
import Image from 'next/image'
import { Button } from '@/components/ui/button'

import { EditThumbnailDialog } from './EditThumbnailDialog'

type ThumbnailCardProps = {
  id: string
  storageUrl: string
  title?: string | null
  createdAt?: string | Date | null
  keywords?: string[] | null
  onDownload?: () => void
  secondaryHref?: string
  priority?: boolean
  onRegenerate?: (newThumbnail: any) => void
}

export function ThumbnailCard({
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
  const [imageError, setImageError] = React.useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = React.useState(false)

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
    setImageError(true)
  }

  const downloadImage = async () => {
    try {
      const response = await fetch(storageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `thumbnail-${Date.now()}.png`;
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
      <div className="bg-secondary-background border-border flex flex-col rounded-lg border p-4">
        <div className="aspect-video w-full overflow-hidden rounded-md bg-background mb-4 relative group">
          {storageUrl && !imageError ? (
            <>
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
            <Button onClick={downloadImage} className="flex-1 bg-primary text-text font-bold hover:bg-opacity-90">
              Download
            </Button>
            {onRegenerate && (
              <Button
                onClick={() => setIsEditDialogOpen(true)}
                variant="outline"
                className="flex-1 border-primary/30 text-primary font-bold hover:bg-primary/10"
              >
                Edit
              </Button>
            )}
          </div>

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

      {onRegenerate && (
        <EditThumbnailDialog
          isOpen={isEditDialogOpen}
          onClose={() => setIsEditDialogOpen(false)}
          thumbnailId={id}
          imageUrl={storageUrl}
          onSuccess={(newThumbnail) => {
            onRegenerate(newThumbnail)
          }}
        />
      )}
    </>
  )
}

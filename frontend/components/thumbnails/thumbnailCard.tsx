'use client'

import * as React from 'react'
import Image from 'next/image'
import { Edit2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { EditThumbnailDialog } from './EditThumbnailDialog'

type ThumbnailCardProps = {
  id: string
  storageUrl: string
  title?: string | null
  createdAt?: string | Date | null
  keywords?: string[] | null
  onDownload?: () => void
  onRegenerate?: (newThumbnail: any) => void
  secondaryHref?: string
  priority?: boolean
}

export function ThumbnailCard({
  id,
  storageUrl,
  title,
  createdAt,
  keywords,
  onDownload,
  onRegenerate,
  secondaryHref,
  priority = false,
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
              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button
                  size="icon"
                  variant="secondary"
                  className="h-8 w-8 bg-background/80 hover:bg-background text-foreground backdrop-blur-sm"
                  onClick={() => setIsEditDialogOpen(true)}
                >
                  <Edit2 className="h-4 w-4" />
                  <span className="sr-only">Edit</span>
                </Button>
              </div>
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
            <Button
              variant="outline"
              className="border-border bg-transparent text-foreground hover:bg-accent hover:text-accent-foreground px-3"
              onClick={() => setIsEditDialogOpen(true)}
            >
              <Edit2 className="h-4 w-4" />
            </Button>
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

      <EditThumbnailDialog
        isOpen={isEditDialogOpen}
        onClose={() => setIsEditDialogOpen(false)}
        thumbnailId={id}
        imageUrl={storageUrl}
        onSuccess={(newThumbnail) => {
          if (onRegenerate) onRegenerate(newThumbnail)
        }}
      />
    </>
  )
}

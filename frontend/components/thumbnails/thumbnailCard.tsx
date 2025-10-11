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

  return (
    <div className="bg-secondary-background border-border flex flex-col rounded-lg border p-4">
      <div className="aspect-video w-full overflow-hidden rounded-md bg-background mb-4">
        <img
          src={storageUrl}
          alt={displayTitle}
          className="h-full w-full object-cover"
          loading="lazy"
        />
      </div>

      <div className="flex flex-col gap-3 flex-grow">
        <div>
          <h3 className="text-text text-lg font-bold">{displayTitle}</h3>
          {formattedDate ? (
            <p className="text-text/70 mt-1 text-sm">{formattedDate}</p>
          ) : null}
        </div>

        {keywordList.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {keywordList.map((keyword) => (
              <span
                key={keyword}
                className="border-border bg-background/40 text-text/80 rounded-full border px-3 py-1 text-xs font-medium"
              >
                {keyword}
              </span>
            ))}
          </div>
        ) : null}
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

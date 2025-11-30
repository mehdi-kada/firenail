'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import api from '@/lib/axios/axios'

interface ThumbnailVersion {
  id: string
  url: string
}

interface EditThumbnailDialogProps {
  isOpen: boolean
  onClose: () => void
  thumbnailId: string
  imageUrl: string
  onSuccess: (newThumbnail: any) => void
}

export function EditThumbnailDialog({
  isOpen,
  onClose,
  thumbnailId,
  imageUrl,
  onSuccess,
}: EditThumbnailDialogProps) {
  const [prompt, setPrompt] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<ThumbnailVersion[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)

  // Initialize history when dialog opens
  useEffect(() => {
    if (isOpen) {
      setHistory([{ id: thumbnailId, url: imageUrl }])
      setCurrentIndex(0)
      setPrompt('')
      setError(null)
    }
  }, [isOpen, thumbnailId, imageUrl])

  if (!isOpen) return null

  const currentVersion = history[currentIndex]

  // Guard against initial render where effect hasn't run yet
  if (!currentVersion) return null

  const canGoPrevious = currentIndex > 0
  const canGoNext = currentIndex < history.length - 1

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    try {
      const response = await api.post(`/api/thumbnails/${currentVersion.id}/regenerate`, {
        prompt,
      })

      // Add new version to history
      const newVersion: ThumbnailVersion = {
        id: response.data.id,
        url: response.data.storage_url,
      }

      setHistory([...history, newVersion])
      setCurrentIndex(history.length) // Move to the new version
      setPrompt('') // Reset prompt
      onSuccess(response.data) // Notify parent component
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to regenerate thumbnail')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handlePrevious = () => {
    if (canGoPrevious) {
      setCurrentIndex(currentIndex - 1)
    }
  }

  const handleNext = () => {
    if (canGoNext) {
      setCurrentIndex(currentIndex + 1)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 animate-in fade-in duration-200 backdrop-blur-sm">
      <div className="bg-card border-border w-full max-w-lg rounded-lg border p-6 shadow-lg animate-in zoom-in-95 duration-200">
        <h2 className="text-xl font-bold mb-4 text-foreground">Edit Thumbnail</h2>

        <div className="relative aspect-video w-full mb-4 overflow-hidden rounded-md bg-background border border-border">
          <Image
            key={currentVersion.url} // Force re-render on URL change
            src={currentVersion.url}
            alt="Thumbnail to edit"
            fill
            className="object-cover"
          />

          {/* Navigation controls */}
          {history.length > 1 && (
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-black/60 backdrop-blur-sm rounded-full px-3 py-1.5">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handlePrevious}
                disabled={!canGoPrevious}
                className="h-7 w-7 p-0 text-white hover:bg-white/20 disabled:opacity-30"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>

              <span className="text-xs text-white font-medium px-2">
                {currentIndex + 1} / {history.length}
              </span>

              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleNext}
                disabled={!canGoNext}
                className="h-7 w-7 p-0 text-white hover:bg-white/20 disabled:opacity-30"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="prompt" className="text-foreground">Modification Instruction</Label>
            <Input
              id="prompt"
              placeholder="e.g. Make the text brighter, change background to blue..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              required
              className="bg-background text-foreground border-input focus-visible:ring-ring"
            />
          </div>

          {error && (
            <p className="text-destructive text-sm">{error}</p>
          )}

          <div className="flex justify-end gap-2 mt-6">
            <Button type="button" variant="ghost" onClick={onClose} disabled={isSubmitting} className="text-foreground hover:bg-accent hover:text-accent-foreground">
              Close
            </Button>
            <Button type="submit" disabled={isSubmitting} className="bg-primary text-primary-foreground hover:bg-primary/90">
              {isSubmitting ? 'Regenerating...' : 'Regenerate'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

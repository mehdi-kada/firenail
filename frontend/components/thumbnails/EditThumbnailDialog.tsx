'use client'

import { useState } from 'react'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import api from '@/lib/axios/axios'

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

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    try {
      const response = await api.post(`/api/thumbnails/${thumbnailId}/regenerate`, {
        prompt,
      })
      onSuccess(response.data)
      onClose()
      setPrompt('') // Reset prompt
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to regenerate thumbnail')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 animate-in fade-in duration-200 backdrop-blur-sm">
      <div className="bg-card border-border w-full max-w-lg rounded-lg border p-6 shadow-lg animate-in zoom-in-95 duration-200">
        <h2 className="text-xl font-bold mb-4 text-foreground">Edit Thumbnail</h2>
        
        <div className="relative aspect-video w-full mb-4 overflow-hidden rounded-md bg-background border border-border">
          <Image
            src={imageUrl}
            alt="Thumbnail to edit"
            fill
            className="object-cover"
          />
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
              Cancel
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

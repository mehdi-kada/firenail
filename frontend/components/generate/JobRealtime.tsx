"use client"

import { useEffect, useState, useMemo } from "react"
import { DotLottieReact } from '@lottiefiles/dotlottie-react'
import { createClient } from "@/lib/supabase/client"
import { CheckCircle2, Loader2 } from "lucide-react"

type JobRealtimeProps = {
  jobId?: string
}

type JobEvent = {
  id: string
  job_id: string
  step: string
  status: string
  payload: Record<string, unknown>
  created_at: string
}

export function JobRealtime({ jobId }: JobRealtimeProps) {
  const [events, setEvents] = useState<JobEvent[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const supabase = createClient()

    if (!jobId) {
      setEvents([])
      setError(null)
      setIsLoading(false)
      return
    }

    let isMounted = true

    const loadEvents = async () => {
      setIsLoading(true)
      const { data, error: fetchError } = await supabase
        .from("job_events")
        .select("id, job_id, step, status, payload, created_at")
        .eq("job_id", jobId)
        .order("created_at", { ascending: true })

      if (!isMounted) return

      if (fetchError) {
        setError("Failed to load job updates.")
      } else if (data) {
        setEvents(data as JobEvent[])
        setError(null)
      }
      setIsLoading(false)
    }

    const channel = supabase
      .channel(`job-events-${jobId}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "job_events",
          filter: `job_id=eq.${jobId}`,
        },
        (payload) => {
          console.log("New job event:", payload)
          if (!payload.new) return
          const newEvent = payload.new as JobEvent
          setEvents((prev) => {
            if (prev.some((event) => event.id === newEvent.id)) {
              return prev
            }
            return [...prev, newEvent].sort(
              (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
            )
          })
        }
      )
      .subscribe((status, err) => {
        if (status === 'SUBSCRIBED') {
          console.log(`Successfully subscribed to job events for ${jobId}`)
          loadEvents()
        }
        if (status === 'CHANNEL_ERROR') {
          console.error('Channel error:', err)
          setError(`Failed to subscribe to updates: ${err.message}`)
        }
      })

    return () => {
      isMounted = false
      supabase.removeChannel(channel)
    }
  }, [jobId])

  const videoTitle = useMemo(() => {
    const metadataEvent = events.find((e) => e.step === "metadata" && e.status === "completed")
    return metadataEvent?.payload?.title as string | undefined
  }, [events])

  const summary = useMemo(() => {
    const analysisEvent = events.find((e) => e.step === "analysis" && e.status === "completed")
    return analysisEvent?.payload?.summary as string | undefined
  }, [events])

  const thumbnailUrl = useMemo(() => {
    const thumbnailEvent = events.find((e) => e.step === "thumbnail" && e.status === "completed")
    return thumbnailEvent?.payload?.url as string | undefined
  }, [events])

  const isCompleted = useMemo(() => {
    return events.some((e) => e.step === "done" && e.status === "completed")
  }, [events])

  const currentStep = useMemo(() => {
    if (!events.length) return null
    const lastEvent = events[events.length - 1]
    return formatStepName(lastEvent.step)
  }, [events])

  if (!jobId) {
    return null
  }

  if (error) {
    return (
      <div className="mt-8 text-center">
        <p className="text-sm text-destructive">{error}</p>
      </div>
    )
  }

  if (isLoading && events.length === 0) {
    return (
      <div className="mt-8 text-center">
        <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
        <p className="mt-4 text-sm text-muted-foreground">Connecting...</p>
      </div>
    )
  }

  return (
    <div className="mt-8 space-y-6">
      {/* Video Title - appears first when metadata is ready */}
      {videoTitle && (
        <div className="text-center space-y-2 animate-in fade-in duration-500">
          <h2 className="text-2xl font-bold text-foreground">{videoTitle}</h2>
        </div>
      )}

      {/* Summary - appears after analysis */}
      {summary && (
        <div className="max-w-2xl mx-auto animate-in fade-in duration-500">
          <p className="text-center text-muted-foreground leading-relaxed">{summary}</p>
        </div>
      )}

      {/* Lottie Animation or Generated Image */}
      <div className="flex items-center justify-center">
        {thumbnailUrl ? (
          <div className="relative group animate-in fade-in duration-700">
            <img
              src={thumbnailUrl}
              alt="Generated Thumbnail"
              className="max-w-2xl w-full h-auto rounded-2xl shadow-2xl border border-border"
            />
            <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Completed
            </div>
          </div>
        ) : (
          <div className="w-full max-w-md">
            <DotLottieReact
              src="https://lottie.host/7b402db5-8d25-42cd-93ef-f65004e61382/66dwbIRr0p.lottie"
              loop
              autoplay
            />
          </div>
        )}
      </div>

      {/* Status Indicator */}
      {!isCompleted && currentStep && (
        <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground animate-pulse">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>{currentStep}</span>
        </div>
      )}

      {/* Minimal Event Timeline */}
      {events.length > 0 && (
        <div className="max-w-xl mx-auto">
          <div className="flex items-center gap-2 flex-wrap justify-center">
            {events
              .filter((e) => ["metadata", "analysis", "thumbnail", "done"].includes(e.step))
              .map((event) => (
                <div
                  key={event.id}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                    event.status === "completed"
                      ? "bg-green-500/10 text-green-600 dark:text-green-400"
                      : event.status === "started" || event.status === "processing"
                      ? "bg-blue-500/10 text-blue-600 dark:text-blue-400"
                      : event.status === "failed"
                      ? "bg-red-500/10 text-red-600 dark:text-red-400"
                      : "bg-muted text-muted-foreground"
                  }`}
                >
                  {event.status === "completed" && <CheckCircle2 className="h-3 w-3" />}
                  {(event.status === "started" || event.status === "processing") && (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  )}
                  <span>{formatStepName(event.step)}</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}

function formatStepName(step: string): string {
  const stepNames: Record<string, string> = {
    job: "Queued",
    metadata: "Fetching Video Info",
    analysis: "Analyzing Content",
    thumbnail: "Generating Thumbnail",
    done: "Complete",
    error: "Error"
  }
  return stepNames[step] || step.charAt(0).toUpperCase() + step.slice(1)
}


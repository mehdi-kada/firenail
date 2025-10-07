"use client"

import { useEffect, useMemo, useState } from "react"
import { DotLottieReact } from "@lottiefiles/dotlottie-react"
import { createClient } from "@/lib/supabase/client"
import { CheckCircle2, Loader2, Download } from "lucide-react"

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
        if (status === "SUBSCRIBED") {
          console.log(`Successfully subscribed to job events for ${jobId}`)
          loadEvents()
        }
        if (status === "CHANNEL_ERROR") {
          console.error("Channel error:", err)
          setError(
            err?.message
              ? `Failed to subscribe to updates: ${err.message}`
              : "Failed to subscribe to updates.",
          )
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

  const activeStepKey = useMemo(() => {
    if (!events.length) return null
    return events[events.length - 1]?.step ?? null
  }, [events])

  const timelineSteps = useMemo(() => {
    const ordered = ["metadata", "analysis", "thumbnail", "done"]
    const latestByStep = [...events].reverse()

    return ordered.map((step) => {
      const eventForStep = latestByStep.find((event) => event.step === step)
      const status = eventForStep?.status
        ? eventForStep.status
        : isCompleted && step === "done"
        ? "completed"
        : "pending"

      return {
        step,
        label: formatStepName(step),
        status,
      }
    })
  }, [events, isCompleted])

  const progress = useMemo(() => {
    if (!events.length) return 0
    if (isCompleted) return 100
    const ordered = ["job", "metadata", "analysis", "thumbnail", "done"]
    const index = activeStepKey ? ordered.indexOf(activeStepKey) : -1
    if (index === -1) return 15
    const value = ((index + 1) / ordered.length) * 100
    return Math.min(95, Math.round(value))
  }, [activeStepKey, events.length, isCompleted])

  const handleDownload = () => {
    if (!thumbnailUrl) return
    
    const link = document.createElement('a')
    link.href = thumbnailUrl
    link.download = `thumbnail-${Date.now()}.jpg`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

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
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
        <p className="mt-4 text-sm text-muted-foreground">Connecting...</p>
      </div>
    )
  }

  return (
    <section className="mt-8">
      <div className="w-full max-w-2xl mx-auto">
        {events.length > 0 && (
          <div className="mb-6 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 text-sm">
              {isCompleted ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              ) : (
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
              )}
              <span className="font-medium">
                {isCompleted ? "Complete" : currentStep ?? "Processing"}
              </span>
            </div>
          </div>
        )}

        {videoTitle && (
          <div className="mb-6 text-center animate-in fade-in duration-500">
            <h2 className="text-xl font-medium mb-2">{videoTitle}</h2>
            <p className="text-sm text-muted-foreground">
              Generating your thumbnail...
            </p>
          </div>
        )}

        {summary && (
          <div className="mb-6 p-4 bg-muted/30 rounded-lg text-sm text-muted-foreground animate-in slide-in-from-bottom-2 duration-500">
            {summary}...
          </div>
        )}

        <div className="relative mb-6 animate-in fade-in duration-700">
          {thumbnailUrl ? (
            <div className="relative group">
              <img
                src={thumbnailUrl}
                alt="Generated Thumbnail"
                className="w-full rounded-xl shadow-md transition-all duration-500 group-hover:shadow-xl"
              />
              {isCompleted && (
                <button
                  onClick={handleDownload}
                  className="absolute bottom-4 right-4 flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg transition-colors duration-200 shadow-lg"
                >
                  <Download className="h-4 w-4" />
                  <span className="text-sm font-medium">Download</span>
                </button>
              )}
            </div>
          ) : (
            <div className="flex justify-center py-8">
              <DotLottieReact
                src="https://lottie.host/7b402db5-8d25-42cd-93ef-f65004e61382/66dwbIRr0p.lottie"
                loop
                autoplay
              />
            </div>
          )}
        </div>
      </div>
    </section>
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


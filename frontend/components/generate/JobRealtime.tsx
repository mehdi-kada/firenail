"use client"

import { useEffect, useMemo, useState } from "react"
import { DotLottieReact } from "@lottiefiles/dotlottie-react"
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
    <section className="mt-10">
      <div className="relative isolate overflow-hidden rounded-3xl border border-border bg-card/80 px-6 py-10 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.6)] backdrop-blur sm:px-10">
        <div className="absolute -top-24 right-10 h-48 w-48 rounded-full bg-primary/15 blur-3xl" aria-hidden />
        <div className="absolute -bottom-32 left-10 h-64 w-64 rounded-full bg-primary/10 blur-3xl" aria-hidden />

        <div className="relative z-10 mx-auto flex max-w-4xl flex-col items-center gap-10 text-center">
          {events.length > 0 ? (
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1 text-xs font-semibold text-primary">
              {isCompleted ? (
                <CheckCircle2 className="h-3.5 w-3.5" />
              ) : (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              )}
              <span>{isCompleted ? "Processing complete" : currentStep ?? "Processing"}</span>
            </div>
          ) : null}

          {videoTitle && (
            <div className="space-y-3 animate-in fade-in duration-500">
              <h2 className="text-3xl font-semibold sm:text-4xl">{videoTitle}</h2>
              <p className="text-sm text-muted-foreground sm:text-base">
                We're preparing your assets in real time. Sit tight while we keep everything in sync.
              </p>
            </div>
          )}

          {summary && (
            <div className="w-full max-w-2xl animate-in slide-in-from-bottom-2 duration-500">
              <blockquote className="rounded-2xl border border-border/70 bg-background/40 px-6 py-5 text-left text-sm leading-relaxed text-muted-foreground shadow-inner sm:text-base">
                {summary}
              </blockquote>
            </div>
          )}

          <div className="w-full max-w-3xl animate-in fade-in duration-700">
            <div className="group relative overflow-hidden rounded-3xl border border-border/70 bg-background/60 p-3 shadow-lg">
              {thumbnailUrl ? (
                <div className="relative overflow-hidden rounded-2xl">
                  <img
                    src={thumbnailUrl}
                    alt="Generated Thumbnail"
                    className="h-auto w-full rounded-2xl object-cover shadow-2xl transition-transform duration-700 group-hover:scale-[1.02]"
                  />
                  <div className="absolute top-4 right-4 inline-flex items-center gap-1.5 rounded-full bg-emerald-500 px-3 py-1 text-xs font-semibold text-emerald-50 shadow-md">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    Completed
                  </div>
                </div>
              ) : (
                <div className="mx-auto w-full max-w-md">
                  <DotLottieReact
                    src="https://lottie.host/7b402db5-8d25-42cd-93ef-f65004e61382/66dwbIRr0p.lottie"
                    loop
                    autoplay
                  />
                </div>
              )}
            </div>
          </div>

          {events.length > 0 ? (
            <div className="w-full max-w-2xl space-y-4">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Progress</span>
                <span>{progress}%</span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-primary transition-all duration-700 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          ) : null}

          {timelineSteps.some((step) => step.status !== "pending") ? (
            <div className="grid w-full max-w-3xl gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {timelineSteps.map((step, index) => {
                const isActive = step.status === "started" || step.status === "processing"
                const isFailed = step.status === "failed"
                const isComplete = step.status === "completed"

                return (
                  <div
                    key={step.step}
                    className="relative flex flex-col items-center gap-3 rounded-2xl border border-border/70 bg-background/40 p-4 text-center shadow-sm transition-transform hover:-translate-y-1"
                  >
                    <div
                      className={`flex size-10 items-center justify-center rounded-full border text-sm font-semibold ${
                        isComplete
                          ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-400"
                          : isFailed
                          ? "border-destructive/40 bg-destructive/10 text-destructive"
                          : isActive
                          ? "border-primary/40 bg-primary/10 text-primary"
                          : "border-border bg-muted text-muted-foreground"
                      }`}
                    >
                      {isComplete ? (
                        <CheckCircle2 className="h-4 w-4" />
                      ) : isFailed ? (
                        <span>!</span>
                      ) : isActive ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <span className="text-xs">{index + 1}</span>
                      )}
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-foreground">{step.label}</p>
                      <p className="text-xs text-muted-foreground capitalize">
                        {step.status === "pending" ? "Pending" : step.status}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : null}
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


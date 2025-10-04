"use client"

import { useEffect, useMemo, useState } from "react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { createClient } from "@/lib/supabase/client"

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

  const latestStatus = useMemo(() => {
    if (!events.length) return null
    const lastEvent = events[events.length - 1]
    return `${lastEvent.step} · ${lastEvent.status}`
  }, [events])

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle className="text-lg">Live Job Updates</CardTitle>
        <CardDescription>
          {jobId ? `Tracking job ${jobId}` : "Updates will appear after you submit a video."}
        </CardDescription>
        {latestStatus && <p className="text-sm font-medium text-primary">{latestStatus}</p>}
      </CardHeader>
      <CardContent>
        {renderContent({ jobId, events, isLoading, error })}
      </CardContent>
    </Card>
  )
}

type ContentProps = {
  jobId?: string
  events: JobEvent[]
  isLoading: boolean
  error: string | null
}

function renderContent({ jobId, events, isLoading, error }: ContentProps) {
  if (!jobId) {
    return <p className="text-sm text-muted-foreground">Submit a video URL to see live job updates.</p>
  }

  if (error) {
    return <p className="text-sm text-destructive">{error}</p>
  }

  if (isLoading && events.length === 0) {
    return <p className="text-sm text-muted-foreground">Loading job activity…</p>
  }

  if (!events.length) {
    return <p className="text-sm text-muted-foreground">Waiting for the job to start processing…</p>
  }

  return (
    <ul className="space-y-3">
      {events.map((event) => (
        <li key={event.id} className="rounded-lg border border-border bg-secondary-background p-3">
          <div className="flex items-center justify-between text-sm font-semibold">
            <span className="capitalize">{event.step}</span>
            <span className="text-xs uppercase tracking-wide text-muted-foreground">
              {formatStatus(event.status)}
            </span>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">{formatTimestamp(event.created_at)}</p>
          {Object.keys(event.payload ?? {}).length > 0 && (
            <pre className="mt-2 whitespace-pre-wrap break-words rounded-md bg-background p-2 text-xs text-muted-foreground">
              {formatPayload(event.payload)}
            </pre>
          )}
        </li>
      ))}
    </ul>
  )
}

function formatPayload(payload: Record<string, unknown>) {
  try {
    return JSON.stringify(payload, null, 2)
  } catch (err) {
    return String(payload)
  }
}

function formatTimestamp(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  return date.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  })
}

function formatStatus(status: string) {
  return status.replace(/_/g, " ")
}


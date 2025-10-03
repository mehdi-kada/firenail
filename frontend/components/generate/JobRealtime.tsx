"use client"

import { useEffect, useMemo, useState } from "react"

import { DotLottieReact } from "@lottiefiles/dotlottie-react"

import { createClient } from "@/lib/supabase/client"

type JobEventPayload = {
  [key: string]: unknown
  url?: string
  thumbnail_url?: string
}

type JobEvent = {
  id: string
  job_id: string
  step: string
  status: string
  payload: JobEventPayload
  created_at: string
}

const pipelineSteps: { key: JobEvent["step"]; label: string }[] = [
  { key: "job", label: "Queueing Magic" },
  { key: "metadata", label: "Exploring Details" },
  { key: "transcript", label: "Capturing Narrative" },
  { key: "analysis", label: "Shaping Direction" },
  { key: "images", label: "Gathering Inspiration" },
  { key: "thumbnail", label: "Crafting Artwork" },
  { key: "done", label: "Final Reveal" },
]

const stepLabelMap = pipelineSteps.reduce<Record<string, string>>((acc, step) => {
  acc[step.key] = step.label
  return acc
}, {})

const statusTone: Record<string, string> = {
  queued: "bg-secondary-background",
  processing: "bg-secondary-background",
  started: "bg-secondary-background",
  completed: "bg-green-50 text-green-700 border-green-200",
  failed: "bg-red-50 text-red-700 border-red-200",
  skipped: "bg-yellow-50 text-yellow-700 border-yellow-200",
}

const statusCopy: Record<string, string> = {
  queued: "Awaiting Launch",
  processing: "In Motion",
  started: "Kicking Off",
  completed: "Wrapped Up",
  failed: "Needs Attention",
  skipped: "Skipped",
}

function formatStatus(status: string) {
  return statusCopy[status] ?? status.replace(/_/g, " ").replace(/\b\w/g, (s) => s.toUpperCase())
}

export function JobRealtime({ jobId }: { jobId?: string | null }) {
  const supabase = useMemo(() => createClient(), [])
  const [events, setEvents] = useState<JobEvent[]>([])
  const [statusByStep, setStatusByStep] = useState<Record<string, JobEvent>>({})
  const [thumbnailUrl, setThumbnailUrl] = useState<string | null>(null)

  useEffect(() => {
    if (!jobId) return

    let isMounted = true

    const syncMetadata = (items: JobEvent[]) => {
      if (!isMounted) return
      setStatusByStep(items.reduce<Record<string, JobEvent>>((acc, ev) => ({ ...acc, [ev.step]: ev }), {}))
      const latestThumb = [...items]
        .reverse()
        .find((ev) => ev.step === "thumbnail" && typeof ev.payload?.url === "string")

      let nextThumbnail: string | null = null
      const thumbValue = latestThumb?.payload?.url
      if (typeof thumbValue === "string") {
        nextThumbnail = thumbValue
      } else {
        const doneEvent = [...items]
          .reverse()
          .find((ev) => ev.step === "done" && typeof ev.payload?.thumbnail_url === "string")
        if (doneEvent && typeof doneEvent.payload?.thumbnail_url === "string") {
          nextThumbnail = doneEvent.payload.thumbnail_url
        }
      }

      setThumbnailUrl(nextThumbnail)
    }

    const loadHistory = async () => {
      const { data, error } = await supabase
        .from("job_events")
        .select("id, job_id, step, status, payload, created_at")
        .eq("job_id", jobId)
        .order("created_at", { ascending: true })
        .limit(200)

      if (isMounted && !error && data) {
        const casted = data as JobEvent[]
        setEvents(casted)
        syncMetadata(casted)
      }
    }

    loadHistory()

    const channel = supabase
      .channel(`job-events-${jobId}`)
      .on(
        "postgres_changes",
        { event: "INSERT", schema: "public", table: "job_events", filter: `job_id=eq.${jobId}` },
        (payload: any) => {
          const ev = payload.new as JobEvent
          setEvents((prev) => {
            const next = [...prev, ev]
            syncMetadata(next)
            return next
          })
        }
      )
      .subscribe()

    return () => {
      isMounted = false
      supabase.removeChannel(channel)
      setEvents([])
      setStatusByStep({})
      setThumbnailUrl(null)
    }
  }, [jobId, supabase])

  if (!jobId) return null

  return (
    <div className="mt-8 space-y-6">
      <div>
        <h3 className="font-semibold mb-2">Creative Pipeline</h3>
        <ul className="space-y-2">
          {pipelineSteps.map(({ key, label }) => {
            const ev = statusByStep[key]
            const stateTone = ev ? statusTone[ev.status] ?? "" : "border-dashed text-muted-foreground"
            return (
              <li
                key={key}
                className={`flex items-center justify-between rounded-md border px-3 py-2 text-sm border-border bg-secondary-background ${stateTone}`}
              >
                <span className="font-medium">{label}</span>
                <span className="text-xs px-2 py-0.5 rounded border bg-background">{ev ? formatStatus(ev.status) : "Pending"}</span>
              </li>
            )
          })}
        </ul>
      </div>

      <div>
        <h3 className="font-semibold mb-2">Live Signals</h3>
        <ul className="text-sm space-y-1 max-h-64 overflow-auto border rounded-md p-3">
          {events.map((e) => (
            <li key={e.id} className="flex items-center justify-between gap-2">
              <span className="font-mono text-[11px] text-muted-foreground">{new Date(e.created_at).toLocaleTimeString()}</span>
              <span className="truncate">{stepLabelMap[e.step] ?? e.step}</span>
              <span className="text-xs px-2 py-0.5 rounded border bg-secondary-background">{formatStatus(e.status)}</span>
            </li>
          ))}
          {events.length === 0 && <li className="text-muted-foreground">Waiting for events…</li>}
        </ul>
      </div>

      <div>
        <h3 className="font-semibold mb-2">Artwork Preview</h3>
        <div className="flex flex-col items-center justify-center rounded-xl border border-border bg-secondary-background p-6">
          {thumbnailUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={thumbnailUrl} alt="Generated thumbnail" className="w-full max-w-xl rounded-lg border shadow-sm" />
          ) : (
            <div className="flex flex-col items-center gap-4 text-center text-sm text-muted-foreground">
              <div className="w-48">
                <DotLottieReact
                  src="https://lottie.host/a074a33e-b10f-4207-b91d-dcb37be041d8/ojYpLFXehX.lottie"
                  loop
                  autoplay
                />
              </div>
              <p className="text-base font-medium text-foreground">Brewing your cinematic thumbnail…</p>
              <p>This usually takes a moment while we refine the final look.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

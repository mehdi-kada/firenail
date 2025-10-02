"use client"

import { useEffect, useMemo, useState } from "react"
import { createClient } from "@/lib/supabase/client"

type JobEvent = {
  id: string
  job_id: string
  step: string
  status: string
  payload: any
  created_at: string
}

export function JobRealtime({ jobId }: { jobId?: string | null }) {
  const supabase = useMemo(() => createClient(), [])
  const [events, setEvents] = useState<JobEvent[]>([])
  const [thumbnailUrl, setThumbnailUrl] = useState<string | null>(null)

  useEffect(() => {
    if (!jobId) return

    let isMounted = true

    const loadHistory = async () => {
      const { data, error } = await supabase
        .from("job_events")
        .select("id, job_id, step, status, payload, created_at")
        .eq("job_id", jobId)
        .order("created_at", { ascending: true })
        .limit(200)

      if (!isMounted) return
      if (!error && data) {
        setEvents(data as JobEvent[])
        const lastThumb = [...data].reverse().find((e: any) => e.step === "thumbnail" && e.payload?.url)
        if (lastThumb) setThumbnailUrl(lastThumb.payload.url)
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
          setEvents((prev) => [...prev, ev])
          if (ev.step === "thumbnail" && ev.payload?.url) setThumbnailUrl(ev.payload.url)
        }
      )
      .subscribe()

    return () => {
      isMounted = false
      supabase.removeChannel(channel)
    }
  }, [jobId, supabase])

  if (!jobId) return null

  return (
    <div className="mt-8 space-y-6">
      <div>
        <h3 className="font-semibold mb-2">Live progress</h3>
        <ul className="text-sm space-y-1 max-h-64 overflow-auto border rounded-md p-3">
          {events.map((e) => (
            <li key={e.id} className="flex items-center justify-between">
              <span className="font-mono text-xs text-muted-foreground">{new Date(e.created_at).toLocaleTimeString()}</span>
              <span className="mx-2">{e.step}</span>
              <span className="text-xs px-2 py-0.5 rounded bg-secondary-background border border-border">{e.status}</span>
            </li>
          ))}
          {events.length === 0 && <li className="text-muted-foreground">Waiting for events…</li>}
        </ul>
      </div>

      {thumbnailUrl && (
        <div>
          <h3 className="font-semibold mb-2">Generated thumbnail</h3>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={thumbnailUrl} alt="Generated thumbnail" className="w-full max-w-xl rounded border" />
        </div>
      )}
    </div>
  )
}

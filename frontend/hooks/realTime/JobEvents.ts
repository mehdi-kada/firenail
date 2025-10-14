import { createClient } from "@/lib/supabase/client"
import { useEffect, useState } from "react"

export type JobEvent = {
  id: string
  job_id: string
  step: string
  status: string
  payload: Record<string, unknown>
  created_at: string
}


export const useJobEvents = (jobId: string | undefined) =>{

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

    return { events, isLoading, error }
}
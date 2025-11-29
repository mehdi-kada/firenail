import { useMemo } from "react"
import { JobEvent } from "./JobEvents"


function formatStepName(step: string, status?: string): string {
  const stepNames: Record<string, string> = {
    job: "Starting",
    metadata: "Loading video data",
    analysis: "Analyzing content",
    images: "Finding images",
    thumbnail: "Creating thumbnail",
    done: "Complete",
    error: "Error"
  }

  const statusSuffix = status === "started" ? "..." : ""
  return (stepNames[step] || step.charAt(0).toUpperCase() + step.slice(1)) + statusSuffix
}



export const useJobState = (events: JobEvent[]) => {

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

  const imageId = useMemo(() => {
    const thumbnailEvent = events.find((e) => e.step === "thumbnail" && e.status === "completed")
    return thumbnailEvent?.payload?.image_id as string | undefined
  }, [events])

  const isCompleted = useMemo(() => {
    return events.some((e) => e.step === "done" && e.status === "completed")
  }, [events])

  const currentStep = useMemo(() => {
    if (!events.length) return null
    const lastEvent = events[events.length - 1]
    return formatStepName(lastEvent.step, lastEvent.status)
  }, [events])

  const activeStepKey = useMemo(() => {
    if (!events.length) return null
    return events[events.length - 1]?.step ?? null
  }, [events])

  const errorEvent = useMemo(() => {
    if (!events.length) return null
    const latest = [...events].reverse()
    return latest.find((event) =>
      event.step === "error" ||
      event.status === "failed" ||
      event.status === "error"
    ) ?? null
  }, [events])

  const jobError = useMemo(() => {
    if (!errorEvent) return null
    const payload = errorEvent.payload ?? {}

    // Check for user_message first
    const userMessage = typeof payload["user_message"] === "string" ? payload["user_message"] : undefined
    if (userMessage) return userMessage

    // Fallback to technical message
    const message = typeof payload["message"] === "string" ? payload["message"] : undefined
    const reason = typeof payload["reason"] === "string" ? payload["reason"] : undefined
    const error = typeof payload["error"] === "string" ? payload["error"] : undefined

    return userMessage ?? message ?? reason ?? error ?? "Something went wrong. Please try again."
  }, [errorEvent])

  const timelineSteps = useMemo(() => {
    const ordered = ["metadata", "analysis", "images", "thumbnail", "done"]
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
        label: formatStepName(step, status),
        status,
      }
    })
  }, [events, isCompleted])

  return {
    isCompleted,
    hasError: Boolean(errorEvent),
    currentStep,
    videoTitle,
    summary,
    thumbnailUrl,
    imageId,
    activeStepKey,
    timelineSteps,
    jobError,
  }

}
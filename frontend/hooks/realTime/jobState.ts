import { useMemo } from "react"
import { JobEvent } from "./JobEvents"


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

  return { isCompleted, currentStep, videoTitle, summary, thumbnailUrl, activeStepKey, timelineSteps }

}
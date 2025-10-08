"use client"

import { useEffect, useMemo, useState } from "react"
import { DotLottieReact } from "@lottiefiles/dotlottie-react"

import { CheckCircle2, Loader2, Download } from "lucide-react"
import { useJobEvents } from "@/hooks/realTime/JobEvents"
import JobStatus from "./JobStatus"

type JobRealtimeProps = {
  jobId?: string
}



export function JobRealtime({ jobId }: JobRealtimeProps) {

  const { events, isLoading, error } = useJobEvents(jobId)



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
        <JobStatus
          events={events}
          isCompleted={isCompleted}
          currentStep={currentStep}
          videoTitle={videoTitle}
          summary={summary}
        />

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


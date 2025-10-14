"use client"

import { useEffect, useRef } from "react"
import { Loader2 } from "lucide-react"
import { useJobEvents } from "@/hooks/realTime/JobEvents"
import { useJobState } from "@/hooks/realTime/jobState"
import JobStatus from "./JobStatus"
import Thumbnail from "./thumbnail"

type JobRealtimeProps = {
  jobId?: string
  onJobComplete?: () => void
  onJobError?: () => void
}



export function JobRealtime({ jobId, onJobComplete, onJobError }: JobRealtimeProps) {

  const { events, isLoading, error } = useJobEvents(jobId)

  const { isCompleted, hasError, currentStep, videoTitle, summary, thumbnailUrl, jobError } = useJobState(events)


  const completionReportedRef = useRef(false)
  const errorReportedRef = useRef(false)

  useEffect(() => {
    completionReportedRef.current = false
    errorReportedRef.current = false
  }, [jobId])

  useEffect(() => {
    if (!jobId) return

    if (hasError && !errorReportedRef.current) {
      onJobError?.()
      errorReportedRef.current = true
    }

    if (isCompleted && !completionReportedRef.current) {
      onJobComplete?.()
      completionReportedRef.current = true
    }
  }, [hasError, isCompleted, jobId, onJobComplete, onJobError])
 


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
          hasEvents={events.length > 0}
          isCompleted={isCompleted}
          hasError={hasError}
          currentStep={currentStep}
          videoTitle={videoTitle}
          summary={summary}
          jobError={jobError}
        />

        {(!hasError || thumbnailUrl) && (
          <Thumbnail
            thumbnailUrl={thumbnailUrl ?? ""}
            isCompleted={isCompleted}
            handleDownload={handleDownload}
          />
        )}
      </div>
    </section>
  )
}



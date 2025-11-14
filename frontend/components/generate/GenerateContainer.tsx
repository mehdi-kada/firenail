"use client"

import { useState, useEffect } from "react"
import { UrlInputForm } from "@/components/generate/urlInputForm"
import { JobRealtime } from "@/components/generate/JobRealtime"
import { createClient } from "@/lib/supabase/client"

const JOB_TIMEOUT_MS = 60000

export function GenerateContainer() {
  const [jobId, setJobId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [hasTimedOut, setHasTimedOut] = useState(false)

  useEffect(() => {
    const checkSession = async () => {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        
      } else {
        
      }
    };
    checkSession();
  }, []);

  useEffect(() => {
    if (!jobId || !isGenerating) {
      setHasTimedOut(false)
      return
    }

    const timeoutId = setTimeout(() => {
      
      setHasTimedOut(true)
      setIsGenerating(false)
    }, JOB_TIMEOUT_MS)

    return () => clearTimeout(timeoutId)
  }, [jobId, isGenerating])

  const handleJobComplete = () => {
    setIsGenerating(false)
    setHasTimedOut(false)
  }

  const handleJobError = () => {
    setIsGenerating(false)
    setHasTimedOut(false)
  }

  return (
    <>
      <UrlInputForm
        onTaskCreated={(id) => {
          setJobId(id)
          setIsGenerating(true)
          setHasTimedOut(false)
        }}
        isGenerating={isGenerating}
      />
      <JobRealtime
        jobId={jobId ?? undefined}
        onJobComplete={handleJobComplete}
        onJobError={handleJobError}
        hasTimedOut={hasTimedOut}
      />
    </>
  )
}

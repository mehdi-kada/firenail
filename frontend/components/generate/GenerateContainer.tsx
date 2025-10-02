"use client"

import { useState } from "react"
import { UrlInputForm } from "@/components/generate/urlInputForm"
import { JobRealtime } from "@/components/generate/JobRealtime"

export function GenerateContainer() {
  const [jobId, setJobId] = useState<string | null>(null)

  return (
    <>
      <UrlInputForm onTaskCreated={(id) => setJobId(id)} />
      <JobRealtime jobId={jobId ?? undefined} />
    </>
  )
}

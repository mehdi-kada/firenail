"use client"

import { useState, useEffect } from "react"
import { UrlInputForm } from "@/components/generate/urlInputForm"
import { JobRealtime } from "@/components/generate/JobRealtime"
import { createClient } from "@/lib/supabase/client"

export function GenerateContainer() {
  const [jobId, setJobId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    const checkSession = async () => {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        console.log("Auth session found on component mount:", session);
      } else {
        console.error("No auth session found. Realtime connection will fail.");
      }
    };
    checkSession();
  }, []);

  return (
    <>
      <UrlInputForm
        onTaskCreated={(id) => {
          setJobId(id)
          setIsGenerating(true)
        }}
        isGenerating={isGenerating}
      />
      <JobRealtime
        jobId={jobId ?? undefined}
        onJobComplete={() => setIsGenerating(false)}
        onJobError={() => setIsGenerating(false)}
      />
    </>
  )
}


import { CheckCircle2, Loader2, XCircle } from "lucide-react"

type JobStatusProps = {
  hasEvents: boolean
  isCompleted: boolean
  hasError: boolean
  currentStep: string | null
  videoTitle?: string
  summary?: string
  jobError?: string | null
}

export default function JobStatus({ hasEvents, isCompleted, hasError, currentStep, videoTitle, summary, jobError }: JobStatusProps) {
  return <>
   {hasEvents && (
          <div className="mb-6 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 text-sm">
              {hasError ? (
                <XCircle className="h-4 w-4 text-destructive" />
              ) : isCompleted ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              ) : (
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
              )}
              <span className="font-medium">
                {hasError ? "Failed" : isCompleted ? "Complete" : currentStep ?? "Processing"}
              </span>
            </div>
          </div>
        )}

        {jobError && (
          <div className="mb-6 rounded-lg border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
            {jobError}
          </div>
        )}

        {videoTitle && !hasError && (
          <div className="mb-6 text-center animate-in fade-in duration-500">
            <h2 className="text-xl font-medium mb-2">{videoTitle}</h2>
            <p className="text-sm text-muted-foreground">
              Generating your thumbnail...
            </p>
          </div>
        )}

        {summary && !hasError && (
          <div className="mb-6 rounded-lg bg-muted/30 p-4 text-sm text-muted-foreground animate-in slide-in-from-bottom-2 duration-500">
            {summary}...
          </div>
        )}
  </>
}
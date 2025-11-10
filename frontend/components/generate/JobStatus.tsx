
import { CheckCircle2, Loader2, XCircle, AlertCircle } from "lucide-react"

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
            <div className="inline-flex items-center gap-2 px-4 py-2 text-sm rounded-full border border-border bg-muted/30">
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
          <div className="mb-6 rounded-lg border border-destructive/40 bg-destructive/10 p-4 text-sm animate-in fade-in duration-300">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-destructive mb-1">Something went wrong</p>
                <p className="text-destructive/90">{jobError}</p>
              </div>
            </div>
          </div>
        )}

        {videoTitle && !hasError && (
          <div className="mb-6 text-center animate-in fade-in duration-500">
            <h2 className="text-xl font-medium mb-2">{videoTitle}</h2>
            <p className="text-sm text-muted-foreground">
              {isCompleted ? "Thumbnail ready!" : "Generating your thumbnail..."}
            </p>
          </div>
        )}

        {summary && !hasError && !isCompleted && (
          <div className="mb-6 rounded-lg bg-muted/30 p-4 text-sm text-muted-foreground animate-in slide-in-from-bottom-2 duration-500">
            <p className="italic">&ldquo;{summary}...&rdquo;</p>
          </div>
        )}
  </>
}

import { JobEvent } from "@/hooks/realTime/JobEvents";
import { CheckCircle2, Loader2 } from "lucide-react"



export default function JobStatus({ events, isCompleted, currentStep, videoTitle, summary }: { events: JobEvent[]; isCompleted: boolean; currentStep: string | null; videoTitle?: string; summary?: string }) {
  return <>
   {events.length > 0 && (
          <div className="mb-6 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 text-sm">
              {isCompleted ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              ) : (
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
              )}
              <span className="font-medium">
                {isCompleted ? "Complete" : currentStep ?? "Processing"}
              </span>
            </div>
          </div>
        )}

        {videoTitle && (
          <div className="mb-6 text-center animate-in fade-in duration-500">
            <h2 className="text-xl font-medium mb-2">{videoTitle}</h2>
            <p className="text-sm text-muted-foreground">
              Generating your thumbnail...
            </p>
          </div>
        )}

        {summary && (
          <div className="mb-6 p-4 bg-muted/30 rounded-lg text-sm text-muted-foreground animate-in slide-in-from-bottom-2 duration-500">
            {summary}...
          </div>
        )}
  </>
}
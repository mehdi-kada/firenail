import { UrlInputForm } from "@/components/generate/urlInputForm";


export default function GeneratePage() {
  return (
    <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl md:text-5xl font-bold tracking-tight">Generate Images from YouTube Videos</h2>
        <p className="mt-4 text-lg text-text/80">Paste a YouTube URL below to get a summary and a generated image based on the video's transcript.</p>
      </div>
      <div className="mt-12 max-w-2xl mx-auto">
        <UrlInputForm />
      </div>
    </main>
  )
}
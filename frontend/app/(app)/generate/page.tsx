import type { Metadata } from "next";
import { GenerateContainer } from "@/components/generate/GenerateContainer";

export const metadata: Metadata = {
  title: "Generate Thumbnail",
  description: "Paste a YouTube URL and let AI generate professional thumbnails based on your video's content. Get stunning covers in seconds.",
  openGraph: {
    title: "Generate YouTube Thumbnails | Firenail",
    description: "Paste a YouTube URL and let AI generate professional thumbnails based on your video's content.",
  },
};

export default function GeneratePage() {
  return (
    <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl md:text-5xl font-bold tracking-tight">Generate Images from YouTube Videos</h2>
        <p className="mt-4 text-lg text-text/80">Paste a YouTube URL below to get a summary and a generated image based on the video's transcript.</p>
      </div>
      <div className="mt-12 max-w-2xl mx-auto">
        <GenerateContainer />
      </div>
    </main>
  )
}
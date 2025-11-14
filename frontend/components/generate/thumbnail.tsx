import { Download } from "lucide-react";
import { DotLottieReact } from "@lottiefiles/dotlottie-react"

export default function Thumbnail({ thumbnailUrl, isCompleted, handleDownload }: { thumbnailUrl: string, isCompleted: boolean, handleDownload: () => void }) {
    const downloadImage = async () => {
      try {
        const response = await fetch(thumbnailUrl);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `thumbnail-${Date.now()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        handleDownload();
      } catch (error) {
        
      }
    };

    return (
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
                  onClick={downloadImage}
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
        </div>)
}
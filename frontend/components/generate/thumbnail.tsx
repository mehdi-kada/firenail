import { useState, useEffect } from "react";
import { Download, Edit2 } from "lucide-react";
import { DotLottieReact } from "@lottiefiles/dotlottie-react"
import { EditThumbnailDialog } from "@/components/thumbnails/EditThumbnailDialog";

export default function Thumbnail({
  thumbnailUrl,
  imageId,
  isCompleted,
  handleDownload
}: {
  thumbnailUrl: string,
  imageId?: string,
  isCompleted: boolean,
  handleDownload: () => void
}) {
  const [currentThumbnailUrl, setCurrentThumbnailUrl] = useState(thumbnailUrl);
  const [currentImageId, setCurrentImageId] = useState(imageId);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  useEffect(() => {
    if (thumbnailUrl) {
      setCurrentThumbnailUrl(thumbnailUrl);
    }
    if (imageId) {
      setCurrentImageId(imageId);
    }
  }, [thumbnailUrl, imageId]);

  const downloadImage = async () => {
    try {
      const response = await fetch(currentThumbnailUrl);
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
      {currentThumbnailUrl ? (
        <div className="relative group">
          <img
            src={currentThumbnailUrl}
            alt="Generated Thumbnail"
            className="w-full rounded-xl shadow-md transition-all duration-500 group-hover:shadow-xl"
          />
          {isCompleted && (
            <div className="absolute bottom-4 right-4 flex gap-2">
              <button
                onClick={downloadImage}
                className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg transition-colors duration-200 shadow-lg"
              >
                <Download className="h-4 w-4" />
                <span className="text-sm font-medium">Download</span>
              </button>
              {currentImageId && (
                <button
                  onClick={() => setIsEditDialogOpen(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-secondary/90 text-secondary-foreground rounded-lg transition-colors duration-200 shadow-lg"
                >
                  <Edit2 className="h-4 w-4" />
                  <span className="text-sm font-medium">Edit</span>
                </button>
              )}
            </div>
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

      {currentImageId && (
        <EditThumbnailDialog
          isOpen={isEditDialogOpen}
          onClose={() => setIsEditDialogOpen(false)}
          thumbnailId={currentImageId}
          imageUrl={currentThumbnailUrl}
          onSuccess={(newThumbnail) => {
            setCurrentThumbnailUrl(newThumbnail.storage_url);
            setCurrentImageId(newThumbnail.id);
          }}
        />
      )}
    </div>)
}
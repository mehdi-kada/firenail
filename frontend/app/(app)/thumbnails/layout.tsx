import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Your Thumbnails",
    description: "Browse and manage all the AI-generated thumbnails you've created for your YouTube videos. Download, regenerate, or edit your thumbnail collection.",
    robots: {
        index: false,
        follow: false,
    },
};

export default function ThumbnailsLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}

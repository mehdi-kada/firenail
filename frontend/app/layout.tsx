import type { Metadata } from "next";
import "./globals.css";

const siteConfig = {
  name: "Firenail",
  description: "AI-powered YouTube thumbnail generator. Transform any YouTube video into stunning, click-worthy thumbnails using AI that understands your content.",
  url: "https://firenail.ai",
};

export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  title: {
    default: "Firenail - AI YouTube Thumbnail Generator",
    template: "%s | Firenail",
  },
  description: siteConfig.description,
  keywords: [
    "YouTube thumbnail generator",
    "AI thumbnail maker",
    "video thumbnail creator",
    "YouTube thumbnail design",
    "AI image generation",
    "content creator tools",
    "thumbnail automation",
    "YouTube SEO",
    "video marketing",
    "thumbnail creator",
  ],
  authors: [{ name: "Firenail" }],
  creator: "Firenail",
  publisher: "Firenail",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: "/favicon.png",
    apple: "/favicon.png",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: siteConfig.url,
    siteName: siteConfig.name,
    title: "Firenail - AI YouTube Thumbnail Generator",
    description: siteConfig.description,
    images: [
      {
        url: "/hero-collage.png",
        width: 1200,
        height: 630,
        alt: "Firenail - AI-powered YouTube thumbnail generator",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Firenail - AI YouTube Thumbnail Generator",
    description: siteConfig.description,
    images: ["/hero-collage.png"],
    creator: "@firenail",
  },
  alternates: {
    canonical: siteConfig.url,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300..700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased bg-background text-foreground font-sans">
        {children}
      </body>
    </html>
  );
}

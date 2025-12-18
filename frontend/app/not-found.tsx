import type { Metadata } from "next";
import Link from 'next/link';

export const metadata: Metadata = {
  title: "Page Not Found",
  description: "The page you're looking for doesn't exist. Return to Firenail to continue creating amazing YouTube thumbnails.",
  robots: {
    index: false,
    follow: true,
  },
};

export default function NotFound() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="flex flex-col items-center gap-6 text-center max-w-2xl">
        {/* 404 with fire icon */}
        <div className="flex items-center justify-center gap-4">
          <h1 className="text-9xl font-bold text-primary">4</h1>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="w-32 h-32 text-primary"
          >
            <path
              fillRule="evenodd"
              d="M12.963 2.286a.75.75 0 0 0-1.071-.136 9.742 9.742 0 0 0-3.539 6.176 7.547 7.547 0 0 1-1.705-1.715.75.75 0 0 0-1.152-.082A9 9 0 1 0 15.68 4.534a7.46 7.46 0 0 1-2.717-2.248ZM15.75 14.25a3.75 3.75 0 1 1-7.313-1.172c.628.465 1.35.81 2.133 1a5.99 5.99 0 0 1 1.925-3.546 3.75 3.75 0 0 1 3.255 3.718Z"
              clipRule="evenodd"
            />
          </svg>
          <h1 className="text-9xl font-bold text-primary">4</h1>
        </div>

        {/* Error message */}
        <div className="flex max-w-md flex-col items-center gap-2">
          <p className="text-foreground text-2xl font-bold leading-tight tracking-[-0.015em]">
            Oops! Page on Fire?
          </p>
          <p className="text-muted-foreground text-base font-normal leading-normal">
            The page you&apos;re looking for seems to have vanished in a puff of smoke. Let&apos;s get you back on track.
          </p>
        </div>

        {/* Back to home button */}
        <Link href="/thumbnails">
          <button className="flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 px-6 bg-primary text-primary-foreground text-sm font-bold leading-normal tracking-[0.015em] hover:opacity-90 transition-opacity">
            <span className="truncate">Go to Homepage</span>
          </button>
        </Link>
      </div>
    </div>
  );
}
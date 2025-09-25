"use client"

import Link from "next/link"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type LandingNavProps = {
	className?: string
}

export function LandingNav({ className }: LandingNavProps) {
	return (
		<header
			className={cn(
				"sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60",
				className,
			)}
		>
			<nav className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
				<Link
					href="/"
					className="flex items-center gap-2 text-base font-semibold text-foreground transition-colors hover:text-primary"
					aria-label="ThumbnailAI home"
				>
					<img
						src="/ChatGPT Image Sep 24, 2025, 08_56_24 PM.png"
						alt="ThumbnailAI Logo"
						className="h-15 w-auto"
					/>
				</Link>

				<div className="flex items-center gap-2 sm:gap-3">
					<Button variant="ghost" className="px-3 sm:px-4" asChild>
						<Link href="/auth/login">Log in</Link>
					</Button>
					<Button className="px-3 sm:px-5" asChild>
						<Link href="/auth/register">Sign up</Link>
					</Button>
				</div>
			</nav>
		</header>
	)
}

export default LandingNav

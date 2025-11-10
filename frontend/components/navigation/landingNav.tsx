"use client"

import { useEffect, useState } from "react"
import Image from "next/image"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { createClient } from "@/lib/supabase/client"

type LandingNavProps = {
	className?: string
}

export function LandingNav({ className }: LandingNavProps) {
	const [user, setUser] = useState<any>(null)

	useEffect(() => {
		const supabase = createClient()

		const checkUser = async () => {
			const {
				data: { user },
			} = await supabase.auth.getUser()
			setUser(user)
		}

		checkUser()

		// Listen for auth changes
		const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
			setUser(session?.user ?? null)
		})

		return () => subscription.unsubscribe()
	}, [])
	return (
		<header className="sticky top-0 z-40 w-full p-4 sm:p-6">
			<div
				className={cn(
					"mx-auto flex h-16 w-full max-w-6xl items-center justify-between rounded-lg border border-border/60 bg-background/80 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/60 sm:px-6 lg:px-8",
					className,
				)}
			>
				<nav className="flex w-full items-center justify-between">
				<Link
					href="/"
					className="flex items-center gap-2 text-base font-semibold text-foreground transition-colors hover:text-primary"
					aria-label="ThumbnailAI home"
				>
				<Image
					src="/ChatGPT-Image-Sep-24_-2025_-08_56_24-PM.svg"
					alt="ThumbnailAI Logo"
					width={55}
					height={55}
					className="h-15"
					priority
				/>
				</Link>

				<div className="flex items-center gap-2 sm:gap-3">
					{user ? (
						<Button className="px-3 sm:px-5" asChild>
							<Link href="/thumbnails">Thumbnails</Link>
						</Button>
					) : (
						<>
							<Button variant="ghost" className="px-3 sm:px-4" asChild>
								<Link href="/auth/login">Log in</Link>
							</Button>
							<Button className="px-3 sm:px-5" asChild>
								<Link href="/auth/register">Sign up</Link>
							</Button>
						</>
					)}
				</div>
			</nav>
			</div>
		</header>
	)
}

export default LandingNav

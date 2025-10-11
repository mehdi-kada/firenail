"use client"

import { useEffect, useRef, useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { usePathname } from "next/navigation"

import { LogoutButton } from "@/components/auth/logoutButton"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { createClient } from "@/lib/supabase/client"

type NavLink = {
	href: string
	label: string
}

const navLinks: NavLink[] = [
	{ href: "/thumbnails", label: "Thumbnails" },
	{ href: "/generate", label: "Generate" },
	{ href: "/upgrade", label: "Upgrade" },
]

export function MainNav() {
	const pathname = usePathname()
	const [mobileOpen, setMobileOpen] = useState(false)
	const [menuOpen, setMenuOpen] = useState(false)
	const menuRef = useRef<HTMLDivElement | null>(null)
	const buttonRef = useRef<HTMLButtonElement | null>(null)
	const [userInitials, setUserInitials] = useState<string>("TG")

	useEffect(() => {
		const supabase = createClient()

		const loadUser = async () => {
			const {
				data: { user },
			} = await supabase.auth.getUser()

			if (user) {
				const identifier = user.user_metadata?.full_name || user.email || user.phone || "User"
				const initials = identifier
					.split(/\s+/)
					.filter(Boolean)
					.map((part: string) => part[0]?.toUpperCase())
					.slice(0, 2)
					.join("")

				setUserInitials(initials || "US")
			}
		}

		loadUser()
	}, [])

	useEffect(() => {
		setMobileOpen(false)
		setMenuOpen(false)
	}, [pathname])

	useEffect(() => {
		const handleClickOutside = (event: MouseEvent) => {
			const target = event.target as Node

			if (
				menuRef.current &&
				!menuRef.current.contains(target) &&
				buttonRef.current &&
				!buttonRef.current.contains(target)
			) {
				setMenuOpen(false)
			}
		}

		document.addEventListener("mousedown", handleClickOutside)

		return () => {
			document.removeEventListener("mousedown", handleClickOutside)
		}
	}, [])

	return (
		<header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
			<div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
				<Link
					href="/thumbnails"
					className="flex items-center gap-3 text-base font-semibold text-foreground transition-colors hover:text-primary"
					aria-label="ThumbnailAI thumbnails"
				>
					<Image
						src="/ChatGPT-Image-Sep-24_-2025_-08_56_24-PM.svg"
						alt="ThumbnailAI Logo"
						width={40}
						height={40}
						className="h-10 w-auto"
						priority
					/>
					<span className="hidden sm:inline-flex text-lg font-semibold">ThumbnailAI</span>
				</Link>

				<nav className="hidden md:flex items-center gap-6 text-sm font-medium">
					{navLinks.map((link) => (
						<Link
							key={link.href}
							href={link.href}
							className={cn(
								"transition-colors text-foreground/70 hover:text-primary",
								pathname.startsWith(link.href) && "text-primary"
							)}
						>
							{link.label}
						</Link>
					))}
				</nav>

				<div className="flex items-center gap-2">
					<Button
						variant="ghost"
						size="icon"
						className="md:hidden"
						onClick={() => setMobileOpen((prev) => !prev)}
						aria-label="Toggle navigation menu"
						aria-expanded={mobileOpen}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							strokeWidth="1.5"
							strokeLinecap="round"
							strokeLinejoin="round"
							className="size-5"
						>
							<path d="M4 6h16" />
							<path d="M4 12h16" />
							<path d="M4 18h16" />
						</svg>
					</Button>

					<div className="relative">
						<button
							ref={buttonRef}
							onClick={() => setMenuOpen((prev) => !prev)}
							className="flex size-10 items-center justify-center rounded-full border border-border bg-card text-sm font-semibold text-foreground transition-colors hover:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
							aria-haspopup="true"
							aria-expanded={menuOpen}
						>
							<span className="select-none">{userInitials}</span>
						</button>

						<div
							ref={menuRef}
							className={cn(
								"absolute right-0 mt-2 w-48 overflow-hidden rounded-lg border border-border bg-card shadow-lg transition data-[state=closed]:pointer-events-none data-[state=closed]:opacity-0 data-[state=closed]:translate-y-1",
								menuOpen ? "data-[state=open]" : "data-[state=closed]"
							)}
							data-state={menuOpen ? "open" : "closed"}
						>
							<div className="py-1 text-sm text-foreground/80">
								<Link
									href="#"
									className="block px-4 py-2 transition-colors hover:bg-background/80 hover:text-primary"
								>
									Profile
								</Link>
								<Link
									href="#"
									className="block px-4 py-2 transition-colors hover:bg-background/80 hover:text-primary"
								>
									Settings
								</Link>
								<div className="border-t border-border/60" />
								<div className="px-4 py-2">
									<LogoutButton />
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			{mobileOpen && (
				<div className="border-b border-border/60 bg-background/95 md:hidden">
					<div className="mx-auto flex w-full max-w-6xl flex-col gap-1 px-4 py-3 text-sm font-medium">
						{navLinks.map((link) => (
							<Link
								key={link.href}
								href={link.href}
								className={cn(
									"rounded-md px-2 py-2 transition-colors hover:bg-card hover:text-primary",
									pathname.startsWith(link.href) && "bg-card text-primary"
								)}
							>
								{link.label}
							</Link>
						))}
					</div>
				</div>
			)}
		</header>
	)
}

export default MainNav

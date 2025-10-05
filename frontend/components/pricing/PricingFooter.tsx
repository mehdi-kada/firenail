const footerLinks = [
  { label: "Terms of Service", href: "#" },
  { label: "Privacy Policy", href: "#" },
  { label: "Contact Us", href: "#" },
]

export function PricingFooter() {
  return (
    <footer className="border-t border-border">
      <div className="container mx-auto flex flex-col items-center justify-between gap-6 px-4 py-10 sm:flex-row sm:px-6 lg:px-8">
        <p className="text-sm text-muted-foreground">
          © {new Date().getFullYear()} TranscribeIt. All rights reserved.
        </p>
        <nav className="flex gap-6 text-sm">
          {footerLinks.map((link) => (
            <a key={link.label} href={link.href} className="transition-colors hover:text-primary">
              {link.label}
            </a>
          ))}
        </nav>
      </div>
    </footer>
  )
}

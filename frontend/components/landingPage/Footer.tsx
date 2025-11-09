'use client';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="flex justify-center border-t border-border bg-muted/30 px-4 py-8 sm:px-8 md:px-10">
      <div className="flex w-full max-w-7xl flex-col items-center gap-6 text-center sm:flex-row sm:justify-between">
        <p className="text-sm text-muted-foreground">© {currentYear} Firenail. All rights reserved.</p>
        <div className="flex items-center gap-4">
          <a className="text-sm text-muted-foreground transition-colors hover:text-foreground" href="/terms">
            Terms of Service
          </a>
          <a className="text-sm text-muted-foreground transition-colors hover:text-foreground" href="/privacy">
            Privacy Policy
          </a>
          <a className="text-sm text-muted-foreground transition-colors hover:text-foreground" href="#contact">
            Contact
          </a>
        </div>
      </div>
    </footer>
  );
}

"use client";

import { Github, Twitter } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

export default function Footer() {
  return (
    <footer className="w-full border-t border-white/10 bg-black/20 backdrop-blur-lg">
      <div className="container mx-auto px-4 md:px-6 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo & Brand */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="relative w-8 h-8 flex items-center justify-center transition-transform group-hover:scale-105 duration-300">
              <Image
                src="/ChatGPT-Image-Sep-24_-2025_-08_56_24-PM.svg"
                alt="Firenail Logo"
                width={32}
                height={32}
                className="object-contain"
              />
            </div>
            <span className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-white/90 to-white/70">
              Firenail
            </span>
          </Link>

          {/* Navigation Links */}
          <nav className="flex items-center gap-8">
            <Link
              href="#"
              className="text-sm font-medium text-muted-foreground hover:text-white transition-colors duration-200"
            >
              Privacy Policy
            </Link>
            <Link
              href="#"
              className="text-sm font-medium text-muted-foreground hover:text-white transition-colors duration-200"
            >
              Terms of Use
            </Link>
          </nav>

          {/* Social Links */}
          <div className="flex items-center gap-4">
            {[
              { icon: Twitter, href: "https://twitter.com/mehdi_kada" },
              { icon: Github, href: "https://github.com/mehdi-kada" }
            ].map((social, i) => (
              <a
                key={i}
                href={social.href}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-full text-muted-foreground hover:text-white hover:bg-white/5 transition-all duration-200"
              >
                <social.icon className="w-5 h-5" />
              </a>
            ))}
          </div>
        </div>

        {/* Copyright - subtly included as it's standard */}
        <div className="mt-8 pt-8 border-t border-white/5 flex justify-center">
          <p className="text-xs text-muted-foreground/50">
            © {new Date().getFullYear()} Firenail. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}

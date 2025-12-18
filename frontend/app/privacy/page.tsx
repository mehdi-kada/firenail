import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
    title: "Privacy Policy",
    description: "Learn how Firenail protects your data and privacy. Read our comprehensive privacy policy covering data collection, usage, and your rights.",
    robots: {
        index: true,
        follow: true,
    },
};

export default function PrivacyPolicy() {
    return (
        <div className="min-h-screen bg-background">
            {/* Header */}
            <header className="w-full border-b border-white/10 bg-black/20 backdrop-blur-lg sticky top-0 z-50">
                <div className="container mx-auto px-4 md:px-6 py-4">
                    <div className="flex items-center justify-between">
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
                        <Link
                            href="/"
                            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-white transition-colors"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            Back to Home
                        </Link>
                    </div>
                </div>
            </header>

            {/* Content */}
            <main className="container mx-auto px-4 md:px-6 py-16 max-w-4xl">
                <div className="space-y-8">
                    <div className="space-y-4">
                        <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-white/90 to-white/70">
                            Privacy Policy
                        </h1>
                        <p className="text-muted-foreground">
                            Last updated: December 18, 2025
                        </p>
                    </div>

                    <div className="prose prose-invert max-w-none space-y-8">
                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">1. Introduction</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                Welcome to Firenail. We respect your privacy and are committed to protecting your personal data.
                                This privacy policy explains how we collect, use, and safeguard your information when you use our
                                AI-powered thumbnail generation service.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">2. Information We Collect</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                We collect information you provide directly to us, including:
                            </p>
                            <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                                <li>Account information (email address, name)</li>
                                <li>Images you upload for thumbnail generation</li>
                                <li>Usage data and interaction with our service</li>
                                <li>Payment information (processed securely by third-party providers)</li>
                            </ul>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">3. How We Use Your Information</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                We use the information we collect to:
                            </p>
                            <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                                <li>Provide, maintain, and improve our thumbnail generation services</li>
                                <li>Process your transactions and send related information</li>
                                <li>Send you technical notices and support messages</li>
                                <li>Respond to your comments, questions, and customer service requests</li>
                                <li>Develop new features and services</li>
                            </ul>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">4. Data Storage and Security</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                We implement appropriate technical and organizational measures to protect your personal data
                                against unauthorized access, alteration, disclosure, or destruction. Your images are processed
                                using secure AI models and are not stored permanently unless you choose to save them.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">5. Data Sharing</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                We do not sell, trade, or rent your personal information to third parties. We may share your
                                data with trusted service providers who assist us in operating our platform, conducting our
                                business, or servicing you, provided they agree to keep this information confidential.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">6. Your Rights</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                Depending on your location, you may have certain rights regarding your personal data, including:
                            </p>
                            <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                                <li>The right to access your personal data</li>
                                <li>The right to rectify inaccurate data</li>
                                <li>The right to request deletion of your data</li>
                                <li>The right to restrict processing of your data</li>
                                <li>The right to data portability</li>
                            </ul>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">7. Cookies</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                We use cookies and similar tracking technologies to track activity on our service and hold
                                certain information. You can instruct your browser to refuse all cookies or to indicate when
                                a cookie is being sent.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">8. Changes to This Policy</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                We may update this privacy policy from time to time. We will notify you of any changes by
                                posting the new privacy policy on this page and updating the &quot;Last updated&quot; date.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">9. Contact Us</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                If you have any questions about this Privacy Policy, please contact us at{" "}
                                <a href="mailto:privacy@firenail.ai" className="text-primary hover:underline">
                                    privacy@firenail.ai
                                </a>
                            </p>
                        </section>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="w-full border-t border-white/10 bg-black/20 backdrop-blur-lg mt-16">
                <div className="container mx-auto px-4 md:px-6 py-8">
                    <div className="flex justify-center">
                        <p className="text-xs text-muted-foreground/50">
                            © {new Date().getFullYear()} Firenail. All rights reserved.
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
}

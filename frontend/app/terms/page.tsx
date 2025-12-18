import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
    title: "Terms of Service",
    description: "Read Firenail's Terms of Service. Understand your rights and responsibilities when using our AI-powered YouTube thumbnail generation platform.",
    robots: {
        index: true,
        follow: true,
    },
};

export default function TermsOfService() {
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
                            Terms of Service
                        </h1>
                        <p className="text-muted-foreground">
                            Last updated: December 18, 2025
                        </p>
                    </div>

                    <div className="prose prose-invert max-w-none space-y-8">
                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">1. Acceptance of Terms</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                By accessing and using Firenail, you accept and agree to be bound by the terms and provisions
                                of this agreement. If you do not agree to these terms, please do not use our service.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">2. Description of Service</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                Firenail is an AI-powered thumbnail generation platform that helps content creators design
                                professional, eye-catching thumbnails for their videos. Our service uses advanced machine
                                learning models to generate and enhance images based on your inputs.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">3. User Accounts</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                To access certain features of our service, you must create an account. You are responsible for:
                            </p>
                            <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                                <li>Maintaining the confidentiality of your account credentials</li>
                                <li>All activities that occur under your account</li>
                                <li>Notifying us immediately of any unauthorized use</li>
                                <li>Providing accurate and complete registration information</li>
                            </ul>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">4. Acceptable Use</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                You agree not to use our service to:
                            </p>
                            <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                                <li>Generate content that is illegal, harmful, or violates third-party rights</li>
                                <li>Upload content containing malware or malicious code</li>
                                <li>Attempt to gain unauthorized access to our systems</li>
                                <li>Use the service to harass, abuse, or harm others</li>
                                <li>Generate misleading or deceptive content</li>
                                <li>Violate any applicable laws or regulations</li>
                            </ul>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">5. Intellectual Property</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                You retain ownership of the original content you upload. For AI-generated thumbnails, you are
                                granted a license to use, modify, and distribute the generated content for personal and
                                commercial purposes. Firenail retains rights to use anonymized data for improving our AI models.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">6. Payment and Subscriptions</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                Certain features require a paid subscription. By subscribing:
                            </p>
                            <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                                <li>You authorize us to charge your payment method on a recurring basis</li>
                                <li>Subscriptions automatically renew unless cancelled before the renewal date</li>
                                <li>Refunds are provided according to our refund policy</li>
                                <li>Prices may change with reasonable notice</li>
                            </ul>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">7. Service Availability</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                We strive to maintain high availability but do not guarantee uninterrupted access. We may
                                temporarily suspend the service for maintenance, updates, or due to circumstances beyond our
                                control. We are not liable for any loss resulting from service interruptions.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">8. Limitation of Liability</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                To the maximum extent permitted by law, Firenail shall not be liable for any indirect,
                                incidental, special, consequential, or punitive damages, including without limitation,
                                loss of profits, data, or other intangible losses resulting from your use of the service.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">9. Termination</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                We reserve the right to suspend or terminate your account at any time for violations of these
                                terms or for any other reason at our sole discretion. Upon termination, your right to use the
                                service will immediately cease.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">10. Changes to Terms</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                We reserve the right to modify these terms at any time. We will provide notice of significant
                                changes. Your continued use of the service after changes constitutes acceptance of the new terms.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">11. Governing Law</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                These terms shall be governed by and construed in accordance with applicable laws, without
                                regard to conflict of law principles.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-2xl font-semibold text-white">12. Contact Us</h2>
                            <p className="text-muted-foreground leading-relaxed">
                                If you have any questions about these Terms of Service, please contact us at{" "}
                                <a href="mailto:legal@firenail.ai" className="text-primary hover:underline">
                                    legal@firenail.ai
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

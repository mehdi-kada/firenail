import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Pricing Plans",
    description: "Choose the perfect Firenail plan for your needs. Simple, transparent pricing for AI-powered YouTube thumbnail generation. Start free, upgrade anytime.",
    openGraph: {
        title: "Pricing Plans | Firenail",
        description: "Simple, transparent pricing for AI-powered YouTube thumbnail generation.",
    },
};

export default function PricingLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}

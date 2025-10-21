import { Check } from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export type PricingCardProps = {
  id: string
  title: string
  price: string
  priceSuffix?: string
  description: string
  features: string[]
  ctaLabel: string
  highlighted?: boolean
  accentLabel?: string
  ctaVariant?: "default" | "outline"
  onCTAClick?: () => void | Promise<void>
  isLoading?: boolean
  disabled?: boolean
}

export function PricingCard({
  title,
  price,
  priceSuffix,
  description,
  features,
  ctaLabel,
  highlighted,
  accentLabel,
  ctaVariant = highlighted ? "default" : "outline",
  onCTAClick,
  isLoading = false,
  disabled = false,
}: PricingCardProps) {
  return (
    <article
      className={cn(
        "relative flex h-full flex-col rounded-2xl border bg-card p-8 text-card-foreground transition-all",
        highlighted
          ? "border-2 border-primary shadow-xl"
          : "border-border hover:-translate-y-1 hover:shadow-lg",
      )}
    >
      {highlighted && accentLabel ? (
        <span className="absolute inset-x-0 -top-3 mx-auto w-fit rounded-full bg-primary px-4 py-1 text-sm font-semibold text-primary-foreground shadow-md">
          {accentLabel}
        </span>
      ) : null}

      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">{title}</h2>
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold">{price}</span>
          {priceSuffix ? (
            <span className="text-sm font-medium text-muted-foreground">
              {priceSuffix}
            </span>
          ) : null}
        </div>
        <p className="text-base text-muted-foreground">{description}</p>
      </div>

      <Button
        variant={ctaVariant}
        className={cn(
          "mt-8 w-full",
          highlighted && ctaVariant === "default"
            ? "bg-primary text-primary-foreground hover:bg-primary/90"
            : "border-primary/60 text-primary hover:border-primary hover:bg-primary/10",
        )}
        onClick={onCTAClick}
        disabled={disabled || isLoading}
      >
        {isLoading ? "Loading..." : ctaLabel}
      </Button>

      <ul className="mt-8 space-y-4 text-sm">
        {features.map((feature) => (
          <li key={feature} className="flex items-start gap-3">
            <span className="mt-0.5">
              <Check className="size-5 text-primary" aria-hidden="true" />
            </span>
            <span>{feature}</span>
          </li>
        ))}
      </ul>
    </article>
  )
}

type PricingHeroProps = {
  title: string
  description: string
}

export function PricingHero({ title, description }: PricingHeroProps) {
  return (
    <section className="text-center">
      <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
        {title}
      </h1>
      <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground">
        {description}
      </p>
    </section>
  )
}

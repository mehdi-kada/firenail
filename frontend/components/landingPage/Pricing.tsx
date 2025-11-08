export default function Pricing() {
  const plans = [
    {
      name: "Monthly",
      description: "Flexible month-to-month subscription.",
      price: 12.99,
      period: "/mo",
      features: [
        "Unlimited video transcripts",
        "Unlimited image generations",
        "Priority email support",
        "Advanced generation options",
      ],
      buttonText: "Subscribe Monthly",
      buttonVariant: "secondary",
      highlighted: false,
    },
    {
      name: "Yearly",
      description: "Save 36% with annual billing.",
      price: 99.99,
      period: "/year",
      features: [
        "Unlimited video transcripts",
        "Unlimited image generations",
        "Priority email support",
        "Advanced generation options",
      ],
      buttonText: "Subscribe Yearly",
      buttonVariant: "primary",
      highlighted: true,
    },
  ];

  return (
    <section className="py-16 sm:py-24 space-y-12">
      {/* Section Header */}
      <div className="text-center px-4">
        <h2 className="text-foreground text-3xl sm:text-4xl font-bold leading-tight tracking-tight">
          Find the Perfect Plan
        </h2>
        <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
          Start for free, or unlock powerful features to take your channel to the next level.
        </p>
      </div>

      {/* Pricing Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 px-4 max-w-3xl mx-auto">
        {plans.map((plan, index) => (
          <div
            key={index}
            className={`flex flex-col rounded-lg p-8 relative transition-all ${
              plan.highlighted
                ? "border-2 border-primary bg-card shadow-lg shadow-primary/20"
                : "border border-border bg-card"
            }`}
          >
            {/* Most Popular Badge */}
            {plan.highlighted && (
              <div className="absolute right-0 top-0 bg-primary px-4 py-1 text-sm font-bold text-white rounded-bl-lg">
                Most Popular
              </div>
            )}

            {/* Plan Name */}
            <h3 className="text-lg font-bold text-foreground mt-4">
              {plan.name}
            </h3>

            {/* Plan Description */}
            <p className="mt-2 text-muted-foreground text-sm">
              {plan.description}
            </p>

            {/* Price */}
            <div className="mt-6">
              <span className="text-4xl font-bold text-foreground">
                ${plan.price}
              </span>
              <span className="text-sm font-normal text-muted-foreground">
                {plan.period}
              </span>
            </div>

            {/* Features List */}
            <ul className="mt-8 space-y-4 flex-grow">
              {plan.features.map((feature, featureIndex) => (
                <li
                  key={featureIndex}
                  className="flex items-center gap-3 text-sm text-foreground"
                >
                  <span className="material-symbols-outlined text-primary text-xl">
                    check_circle
                  </span>
                  {feature}
                </li>
              ))}
            </ul>

            {/* CTA Button */}
            <button
              className={`mt-8 w-full rounded-full py-3 font-bold transition-all ${
                plan.highlighted
                  ? "bg-primary text-primary-foreground hover:opacity-90"
                  : "bg-primary/20 text-primary hover:bg-primary/30"
              }`}
            >
              {plan.buttonText}
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}

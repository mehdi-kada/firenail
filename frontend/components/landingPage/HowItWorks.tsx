export default function HowItWorks() {
  const steps = [
    {
      number: "1",
      title: "Provide Your Video Idea",
      description: "Simply enter your video title, a brief description, or a few keywords.",
    },
    {
      number: "2",
      title: "AI Generates Options",
      description: "Our AI analyzes your input and generates a variety of eye-catching thumbnail concepts.",
    },
    {
      number: "3",
      title: "Pick & Publish",
      description: "Choose your favorite design, make optional tweaks, and download it instantly.",
    },
  ];

  return (
    <section className="py-16 sm:py-24 space-y-12">
      {/* Section Header */}
      <div className="text-center px-4">
        <h2 className="text-foreground text-3xl sm:text-4xl font-bold leading-tight tracking-tight">
          How It Works
        </h2>
        <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
          Generate stunning thumbnails in three simple steps.
        </p>
      </div>

      {/* Steps Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 px-4 mx-auto">
        {steps.map((step, index) => (
          <div
            key={index}
            className="flex flex-col items-center gap-4 text-center"
          >
            {/* Step Number Circle */}
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/20 text-primary">
              <span className="text-3xl font-black">{step.number}</span>
            </div>

            {/* Step Title */}
            <h3 className="text-xl font-bold text-foreground">
              {step.title}
            </h3>

            {/* Step Description */}
            <p className="text-sm text-muted-foreground">
              {step.description}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

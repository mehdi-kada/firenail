import type { Metadata } from "next";
import { SignUpForm } from "@/components/auth/registerForm";

export const metadata: Metadata = {
  title: "Create Account",
  description: "Create your free Firenail account and start generating stunning AI-powered YouTube thumbnails today.",
  robots: {
    index: true,
    follow: true,
  },
};

export default function Register() {
  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <SignUpForm />
      </div>
    </div>
  );
}

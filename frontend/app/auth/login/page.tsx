import type { Metadata } from "next";
import { LoginForm } from "@/components/auth/loginForm";

export const metadata: Metadata = {
  title: "Sign In",
  description: "Sign in to your Firenail account to generate AI-powered YouTube thumbnails.",
  robots: {
    index: true,
    follow: true,
  },
};

export default function Login() {
  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <LoginForm />
      </div>
    </div>
  );
}
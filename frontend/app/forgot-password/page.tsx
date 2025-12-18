import type { Metadata } from "next";
import { ForgotPasswordForm } from "@/components/auth/forgotPasswordFrom";

export const metadata: Metadata = {
  title: "Reset Password",
  description: "Reset your Firenail account password to regain access to your AI thumbnail generation tools.",
  robots: {
    index: false,
    follow: false,
  },
};

export default function forgotPasswordPage() {
  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <ForgotPasswordForm />
      </div>
    </div>
  )
}
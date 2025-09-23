import { LogoutButton } from "@/components/auth/logoutButton";

export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <p>Welcome to your dashboard!</p>
      <LogoutButton />
    </div>
  );
}
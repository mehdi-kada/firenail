"use client";
import { LogoutButton } from "@/components/auth/logoutButton";
import api from "@/lib/axios/axios";
import { useEffect } from "react";

export default function DashboardPage() {
  useEffect( () => {
    const fetchData = async () => {
      try {
        const response = await api.get("/")
        console.log(response);
        console.log("Data fetched successfully", response.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    }
    fetchData();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <p>Welcome to your dashboard!</p>
      <LogoutButton />
    </div>
  );
}
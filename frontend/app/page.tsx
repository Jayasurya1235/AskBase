"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type BackendStatus = "checking" | "online" | "offline";

export default function Home() {
  const [status, setStatus] = useState<BackendStatus>("checking");
  const [serviceName, setServiceName] = useState<string>("");

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => {
        if (!res.ok) throw new Error("Backend responded with an error");
        return res.json();
      })
      .then((data) => {
        setServiceName(data.service);
        setStatus("online");
      })
      .catch(() => setStatus("offline"));
  }, []);

  const statusColor =
    status === "online"
      ? "bg-green-500"
      : status === "offline"
        ? "bg-red-500"
        : "bg-yellow-500";

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 px-6">
      <h1 className="text-3xl font-semibold">DBReport AI</h1>
      <p className="max-w-md text-center text-gray-500">
        Phase 1 checkpoint: this page confirms the Next.js frontend can reach
        the FastAPI backend before any real features are built.
      </p>

      <div className="flex items-center gap-3 rounded-lg border border-gray-300 px-5 py-3">
        <span className={`h-2.5 w-2.5 rounded-full ${statusColor}`} />
        <span className="text-sm">
          {status === "checking" && "Checking backend connection..."}
          {status === "online" && `Connected to ${serviceName} backend`}
          {status === "offline" &&
            "Backend not reachable — is uvicorn running?"}
        </span>
      </div>
    </main>
  );
}

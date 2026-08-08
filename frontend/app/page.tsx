"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type SourceType = "file" | "cloud";
type ConnectionState = "idle" | "connecting" | "success" | "error";

type SavedConnection = {
  id: number;
  name: string;
  db_type: string;
  host: string;
  database: string;
};

export default function ConnectPage() {
  const router = useRouter();

  const [sourceType, setSourceType] = useState<SourceType>("file");
  const [isDragging, setIsDragging] = useState(false);
  const [state, setState] = useState<ConnectionState>("idle");
  const [message, setMessage] = useState("");

  const [dbType, setDbType] = useState<"mysql" | "postgresql">("mysql");
  const [host, setHost] = useState("");
  const [port, setPort] = useState("3306");
  const [database, setDatabase] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [connectionName, setConnectionName] = useState("");
  const [savedConnections, setSavedConnections] = useState<SavedConnection[]>(
    [],
  );

  // Load the list of previously saved connections when the page opens
  useEffect(() => {
    fetch(`${API_URL}/saved-connections/`)
      .then((res) => res.json())
      .then(setSavedConnections)
      .catch(() => setSavedConnections([]));
  }, []);

  async function handleConnect() {
    setState("connecting");
    setMessage("");

    try {
      const res = await fetch(`${API_URL}/connections/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          db_type: dbType,
          host,
          port: Number(port),
          username,
          password,
          database,
        }),
      });

      const data = await res.json();

      if (data.success) {
        setState("success");
        setMessage(data.message);

        // Fetch the schema now, so the dashboard can display it right
        // after redirect — sessionStorage is fine here since it's just
        // UI display data, cleared when the tab closes.
        try {
          const schemaRes = await fetch(`${API_URL}/connections/schema`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              db_type: dbType,
              host,
              port: Number(port),
              username,
              password,
              database,
            }),
          });
          const schemaData = await schemaRes.json();
          sessionStorage.setItem("askbase_schema", JSON.stringify(schemaData));
        } catch {
          // Schema fetch failing shouldn't block the redirect.
        }
        sessionStorage.setItem(
          "askbase_connection",
          JSON.stringify({
            db_type: dbType,
            host,
            port: Number(port),
            username,
            password,
            database,
          }),
        );
        // If the user gave this connection a name, save it (encrypted)
        // before redirecting.
        if (connectionName.trim()) {
          await fetch(
            `${API_URL}/saved-connections/?name=${encodeURIComponent(connectionName)}`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                db_type: dbType,
                host,
                port: Number(port),
                username,
                password,
                database,
              }),
            },
          );
        }

        setTimeout(() => router.push("/dashboard"), 1200);
      } else {
        setState("error");
        setMessage(data.message);
      }
    } catch {
      setState("error");
      setMessage("Could not reach the backend. Is the server running?");
    }
  }

  function handleUseSaved(conn: SavedConnection) {
    setSourceType("cloud");
    setDbType(conn.db_type as "mysql" | "postgresql");
    setHost(conn.host);
    setDatabase(conn.database);
    // Password is never sent back from the server — the user re-enters
    // it here. A later phase can add a "reconnect by id" endpoint that
    // decrypts server-side and skips this step entirely.
    setMessage(
      `Loaded "${conn.name}" — please re-enter the password to reconnect.`,
    );
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      setMessage(
        `"${file.name}" selected — file upload isn't wired up yet (Phase 2 continued).`,
      );
    }
  }

  return (
    <main className="min-h-screen bg-[#0b0d10] text-white flex flex-col items-center justify-center px-6 py-16">
      <div className="mb-3 flex items-center gap-2">
        <span className="h-6 w-6 rounded bg-gradient-to-br from-violet-400 to-fuchsia-500" />
        <span className="text-lg font-semibold tracking-tight">AskBase</span>
      </div>

      <h1 className="text-3xl md:text-4xl font-bold text-center mb-2">
        Make Your Data a Report
      </h1>
      <p className="text-neutral-400 text-center mb-6 max-w-md">
        Connect a database or drop a file — AskBase reads the schema and gets
        you ready to ask questions in plain English.
      </p>

      {savedConnections.length > 0 && (
        <div className="w-full max-w-md mb-6">
          <p className="text-xs text-neutral-500 mb-2 uppercase tracking-wide">
            Saved connections
          </p>
          <div className="flex flex-col gap-2">
            {savedConnections.map((conn) => (
              <button
                key={conn.id}
                onClick={() => handleUseSaved(conn)}
                className="flex items-center justify-between rounded-lg bg-white/5 border border-white/10 px-4 py-2 text-sm hover:bg-white/10 transition text-left"
              >
                <span>{conn.name}</span>
                <span className="text-neutral-500 text-xs">
                  {conn.db_type} · {conn.database}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-2 mb-6 rounded-full bg-white/5 p-1 border border-white/10">
        <button
          onClick={() => setSourceType("file")}
          className={`px-5 py-2 rounded-full text-sm font-medium transition ${
            sourceType === "file"
              ? "bg-violet-500 text-white"
              : "text-neutral-400"
          }`}
        >
          Local File
        </button>
        <button
          onClick={() => setSourceType("cloud")}
          className={`px-5 py-2 rounded-full text-sm font-medium transition ${
            sourceType === "cloud"
              ? "bg-violet-500 text-white"
              : "text-neutral-400"
          }`}
        >
          Cloud Database
        </button>
      </div>

      {sourceType === "file" ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={`w-full max-w-2xl rounded-3xl border-2 border-dashed px-8 py-14 text-center transition ${
            isDragging
              ? "border-violet-400 bg-violet-500/10"
              : "border-white/15 bg-white/5"
          }`}
        >
          <p className="text-lg font-medium mb-1">Drop your data file here</p>
          <p className="text-sm text-neutral-500">
            CSV, XLSX, JSON, SQL dump — or click to browse
          </p>
        </div>
      ) : (
        <div className="w-full max-w-md rounded-3xl bg-white/5 border border-white/10 p-8">
          <div className="grid grid-cols-2 gap-3 mb-3">
            <select
              value={dbType}
              onChange={(e) =>
                setDbType(e.target.value as "mysql" | "postgresql")
              }
              className="col-span-2 bg-white/10 border border-white/10 rounded-lg px-3 py-2 text-sm"
            >
              <option value="mysql">MySQL</option>
              <option value="postgresql">PostgreSQL</option>
            </select>

            <input
              placeholder="Host"
              value={host}
              onChange={(e) => setHost(e.target.value)}
              className="bg-white/10 border border-white/10 rounded-lg px-3 py-2 text-sm placeholder:text-neutral-500"
            />
            <input
              placeholder="Port"
              value={port}
              onChange={(e) => setPort(e.target.value)}
              className="bg-white/10 border border-white/10 rounded-lg px-3 py-2 text-sm placeholder:text-neutral-500"
            />
            <input
              placeholder="Database name"
              value={database}
              onChange={(e) => setDatabase(e.target.value)}
              className="col-span-2 bg-white/10 border border-white/10 rounded-lg px-3 py-2 text-sm placeholder:text-neutral-500"
            />
            <input
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="bg-white/10 border border-white/10 rounded-lg px-3 py-2 text-sm placeholder:text-neutral-500"
            />
            <input
              placeholder="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-white/10 border border-white/10 rounded-lg px-3 py-2 text-sm placeholder:text-neutral-500"
            />
          </div>

          <input
            placeholder="Name this connection to save it (optional)"
            value={connectionName}
            onChange={(e) => setConnectionName(e.target.value)}
            className="w-full bg-white/10 border border-white/10 rounded-lg px-3 py-2 text-sm placeholder:text-neutral-500 mb-4"
          />

          <button
            onClick={handleConnect}
            disabled={state === "connecting"}
            className="w-full rounded-lg bg-violet-500 hover:bg-violet-400 transition py-2.5 text-sm font-semibold disabled:opacity-50"
          >
            {state === "connecting" ? "Connecting..." : "Connect"}
          </button>
        </div>
      )}

      {message && (
        <p
          className={`mt-5 text-sm ${
            state === "success"
              ? "text-green-400"
              : state === "error"
                ? "text-red-400"
                : "text-neutral-400"
          }`}
        >
          {message}
        </p>
      )}
    </main>
  );
}

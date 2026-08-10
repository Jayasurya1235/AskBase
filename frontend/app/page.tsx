"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ThemeToggle from "./components/ThemeToggle";

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
    setMessage(
      `Loaded "${conn.name}" — please re-enter the password to reconnect.`,
    );
  }

  async function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    await handleFileUpload(file);
  }

  async function handleFileUpload(file: File) {
    setState("connecting");
    setMessage(`Uploading "${file.name}"...`);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await fetch(`${API_URL}/upload/file`, {
        method: "POST",
        body: formData,
      });

      const uploadData = await uploadRes.json();

      if (!uploadRes.ok) {
        setState("error");
        setMessage(uploadData.detail || "Upload failed.");
        return;
      }

      const connection = {
        db_type: uploadData.db_type,
        host: uploadData.host,
        port: uploadData.port,
        username: uploadData.username,
        password: uploadData.password,
        database: uploadData.database,
      };

      const schemaRes = await fetch(`${API_URL}/connections/schema`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(connection),
      });
      const schemaData = await schemaRes.json();
      sessionStorage.setItem("askbase_schema", JSON.stringify(schemaData));
      sessionStorage.setItem("askbase_connection", JSON.stringify(connection));

      setState("success");
      setMessage(uploadData.message);
      setTimeout(() => router.push("/dashboard"), 1000);
    } catch {
      setState("error");
      setMessage("Could not reach the backend. Is the server running?");
    }
  }

  const inputStyle = {
    backgroundColor: "var(--bg-app)",
    borderColor: "var(--border-color)",
    color: "var(--text-primary)",
  };

  return (
    <main
      className="min-h-screen flex flex-col items-center justify-center px-6 py-16 relative"
      style={{ backgroundColor: "var(--bg-app)", color: "var(--text-primary)" }}
    >
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      <div className="mb-3 flex items-center gap-2">
        <span className="h-6 w-6 rounded bg-gradient-to-br from-violet-400 to-fuchsia-500" />
        <span className="text-lg font-semibold tracking-tight">AskBase</span>
      </div>

      <h1 className="text-3xl md:text-4xl font-bold text-center mb-2">
        Make Your Data a Report
      </h1>
      <p
        className="text-center mb-6 max-w-md"
        style={{ color: "var(--text-secondary)" }}
      >
        Connect a database or drop a file — AskBase reads the schema and gets
        you ready to ask questions in plain English.
      </p>

      {savedConnections.length > 0 && (
        <div className="w-full max-w-md mb-6">
          <p
            className="text-xs mb-2 uppercase tracking-wide"
            style={{ color: "var(--text-secondary)" }}
          >
            Saved connections
          </p>
          <div className="flex flex-col gap-2">
            {savedConnections.map((conn) => (
              <button
                key={conn.id}
                onClick={() => handleUseSaved(conn)}
                className="flex items-center justify-between rounded-lg border px-4 py-2 text-sm transition text-left hover:opacity-80"
                style={{
                  backgroundColor: "var(--bg-surface)",
                  borderColor: "var(--border-color)",
                }}
              >
                <span>{conn.name}</span>
                <span
                  className="text-xs"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {conn.db_type} · {conn.database}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div
        className="flex gap-2 mb-6 rounded-full p-1 border"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-color)",
        }}
      >
        <button
          onClick={() => setSourceType("file")}
          className={`px-5 py-2 rounded-full text-sm font-medium transition ${
            sourceType === "file" ? "bg-violet-500 text-white" : ""
          }`}
          style={
            sourceType !== "file"
              ? { color: "var(--text-secondary)" }
              : undefined
          }
        >
          Local File
        </button>
        <button
          onClick={() => setSourceType("cloud")}
          className={`px-5 py-2 rounded-full text-sm font-medium transition ${
            sourceType === "cloud" ? "bg-violet-500 text-white" : ""
          }`}
          style={
            sourceType !== "cloud"
              ? { color: "var(--text-secondary)" }
              : undefined
          }
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
          className="w-full max-w-2xl rounded-3xl border-2 border-dashed px-8 py-14 text-center transition"
          style={{
            borderColor: isDragging ? "#a78bfa" : "var(--border-color)",
            backgroundColor: isDragging
              ? "rgba(139,92,246,0.1)"
              : "var(--bg-surface)",
          }}
        >
          <p className="text-lg font-medium mb-1">Drop your data file here</p>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            CSV, XLSX, JSON, SQL dump — or click to browse
          </p>
        </div>
      ) : (
        <div
          className="w-full max-w-md rounded-3xl border p-8"
          style={{
            backgroundColor: "var(--bg-surface)",
            borderColor: "var(--border-color)",
          }}
        >
          <div className="grid grid-cols-2 gap-3 mb-3">
            <select
              value={dbType}
              onChange={(e) =>
                setDbType(e.target.value as "mysql" | "postgresql")
              }
              className="col-span-2 border rounded-lg px-3 py-2 text-sm"
              style={inputStyle}
            >
              <option value="mysql">MySQL</option>
              <option value="postgresql">PostgreSQL</option>
            </select>

            <input
              placeholder="Host"
              value={host}
              onChange={(e) => setHost(e.target.value)}
              className="border rounded-lg px-3 py-2 text-sm"
              style={inputStyle}
            />
            <input
              placeholder="Port"
              value={port}
              onChange={(e) => setPort(e.target.value)}
              className="border rounded-lg px-3 py-2 text-sm"
              style={inputStyle}
            />
            <input
              placeholder="Database name"
              value={database}
              onChange={(e) => setDatabase(e.target.value)}
              className="col-span-2 border rounded-lg px-3 py-2 text-sm"
              style={inputStyle}
            />
            <input
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="border rounded-lg px-3 py-2 text-sm"
              style={inputStyle}
            />
            <input
              placeholder="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="border rounded-lg px-3 py-2 text-sm"
              style={inputStyle}
            />
          </div>

          <input
            placeholder="Name this connection to save it (optional)"
            value={connectionName}
            onChange={(e) => setConnectionName(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm mb-4"
            style={inputStyle}
          />

          <button
            onClick={handleConnect}
            disabled={state === "connecting"}
            className="w-full rounded-lg bg-violet-500 hover:bg-violet-400 transition py-2.5 text-sm font-semibold disabled:opacity-50 text-white"
          >
            {state === "connecting" ? "Connecting..." : "Connect"}
          </button>
        </div>
      )}

      {message && (
        <p
          className={`mt-5 text-sm ${
            state === "success"
              ? "text-green-500"
              : state === "error"
                ? "text-red-500"
                : ""
          }`}
          style={
            state === "idle" || state === "connecting"
              ? { color: "var(--text-secondary)" }
              : undefined
          }
        >
          {message}
        </p>
      )}
    </main>
  );
}

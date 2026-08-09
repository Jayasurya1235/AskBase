"use client";

import { useState, useEffect, useRef } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Message = {
  role: "user" | "assistant";
  content: string;
  sql?: string;
  columns?: string[];
  rows?: Record<string, unknown>[];
  rowCount?: number;
  error?: boolean;
};

function isChartable(columns?: string[], rows?: Record<string, unknown>[]) {
  if (!columns || !rows || columns.length !== 2 || rows.length === 0)
    return false;
  const [colA, colB] = columns;
  const sample = rows[0];
  const aIsNumber =
    typeof sample[colA] === "number" || !isNaN(Number(sample[colA]));
  const bIsNumber =
    typeof sample[colB] === "number" || !isNaN(Number(sample[colB]));
  return aIsNumber !== bIsNumber;
}

async function downloadExport(
  format: "excel" | "pdf",
  question: string,
  columns: string[],
  rows: Record<string, unknown>[],
) {
  const res = await fetch(`${API_URL}/export/${format}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, columns, rows }),
  });

  if (!res.ok) return;

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `askbase_export.${format === "excel" ? "xlsx" : "pdf"}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

function MessageResult({
  question,
  columns,
  rows,
}: {
  question: string;
  columns: string[];
  rows: Record<string, unknown>[];
}) {
  const [view, setView] = useState<"table" | "chart">("table");
  const chartable = isChartable(columns, rows);

  const [textCol, numCol] = (() => {
    if (!chartable) return [columns[0], columns[1]];
    const sample = rows[0];
    const aIsNumber =
      typeof sample[columns[0]] === "number" ||
      !isNaN(Number(sample[columns[0]]));
    return aIsNumber ? [columns[1], columns[0]] : [columns[0], columns[1]];
  })();

  const chartData = rows.slice(0, 20).map((row) => ({
    name: String(row[textCol]),
    value: Number(row[numCol]),
  }));

  return (
    <div className="mt-3">
      <div className="flex gap-1 mb-2 flex-wrap">
        {chartable && (
          <>
            <button
              onClick={() => setView("table")}
              className={`text-xs px-2.5 py-1 rounded-md transition ${
                view === "table"
                  ? "bg-violet-500 text-white"
                  : "bg-white/5 text-neutral-400"
              }`}
            >
              Table
            </button>
            <button
              onClick={() => setView("chart")}
              className={`text-xs px-2.5 py-1 rounded-md transition ${
                view === "chart"
                  ? "bg-violet-500 text-white"
                  : "bg-white/5 text-neutral-400"
              }`}
            >
              Chart
            </button>
          </>
        )}
        <button
          onClick={() => downloadExport("excel", question, columns, rows)}
          className="text-xs px-2.5 py-1 rounded-md bg-white/5 text-neutral-400 hover:bg-white/10 transition"
        >
          ⬇ Excel
        </button>
        <button
          onClick={() => downloadExport("pdf", question, columns, rows)}
          className="text-xs px-2.5 py-1 rounded-md bg-white/5 text-neutral-400 hover:bg-white/10 transition"
        >
          ⬇ PDF
        </button>
      </div>

      {view === "table" || !chartable ? (
        <div className="overflow-x-auto">
          <table className="text-xs w-full border-collapse">
            <thead>
              <tr className="text-left text-neutral-500 border-b border-white/10">
                {columns.map((col) => (
                  <th key={col} className="pb-1.5 pr-4">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.slice(0, 20).map((row, ri) => (
                <tr key={ri} className="border-b border-white/5">
                  {columns.map((col) => (
                    <td key={col} className="py-1.5 pr-4 text-neutral-300">
                      {String(row[col])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ width: "100%", height: 240 }}>
          <ResponsiveContainer>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
              <XAxis dataKey="name" tick={{ fill: "#a3a3a3", fontSize: 11 }} />
              <YAxis tick={{ fill: "#a3a3a3", fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  background: "#14171c",
                  border: "1px solid #ffffff20",
                }}
                labelStyle={{ color: "#fff" }}
              />
              <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [connectionMissing, setConnectionMissing] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const conn = sessionStorage.getItem("askbase_connection");
    if (!conn) setConnectionMissing(true);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleAsk() {
    const question = input.trim();
    if (!question || loading) return;

    const connectionRaw = sessionStorage.getItem("askbase_connection");
    if (!connectionRaw) {
      setConnectionMissing(true);
      return;
    }
    const connection = JSON.parse(connectionRaw);

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/query/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, connection }),
      });

      const data = await res.json();

      if (!res.ok) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: data.detail || "Something went wrong.",
            error: true,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Found ${data.row_count} result${data.row_count === 1 ? "" : "s"}.`,
            sql: data.generated_sql,
            columns: data.columns,
            rows: data.rows,
            rowCount: data.row_count,
          },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Could not reach the backend. Is the server running?",
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  if (connectionMissing) {
    return (
      <main className="min-h-screen bg-[#0b0d10] text-white flex items-center justify-center px-6">
        <div className="text-center">
          <p className="text-neutral-300 mb-2">No active connection found.</p>
          <a href="/" className="text-violet-400 hover:underline text-sm">
            Go connect a database first
          </a>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#0b0d10] text-white flex flex-col">
      <header className="border-b border-white/10 px-6 py-4">
        <span className="text-lg font-semibold">AskBase Chat</span>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-6 max-w-3xl w-full mx-auto">
        {messages.length === 0 && (
          <p className="text-neutral-500 text-sm">
            Ask something like &quot;top 5 best selling artists&quot; or
            &quot;how many customers do we have&quot;.
          </p>
        )}

        <div className="flex flex-col gap-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`rounded-2xl px-4 py-3 max-w-2xl ${
                  msg.role === "user"
                    ? "bg-violet-500 text-white"
                    : msg.error
                      ? "bg-red-500/10 border border-red-500/30 text-red-300"
                      : "bg-white/5 border border-white/10"
                }`}
              >
                <p className="text-sm">{msg.content}</p>

                {msg.sql && (
                  <pre className="mt-3 text-xs bg-black/40 rounded-lg p-3 overflow-x-auto text-neutral-400">
                    {msg.sql}
                  </pre>
                )}

                {msg.columns && msg.rows && msg.rows.length > 0 && (
                  <MessageResult
                    question={
                      messages[i - 1]?.role === "user"
                        ? messages[i - 1].content
                        : msg.content
                    }
                    columns={msg.columns}
                    rows={msg.rows}
                  />
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl px-4 py-3 bg-white/5 border border-white/10">
                <p className="text-sm text-neutral-400">Thinking...</p>
              </div>
            </div>
          )}
        </div>
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-white/10 p-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            placeholder="Ask a question about your data..."
            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm placeholder:text-neutral-500"
          />
          <button
            onClick={handleAsk}
            disabled={loading}
            className="bg-violet-500 hover:bg-violet-400 transition rounded-xl px-5 py-3 text-sm font-semibold disabled:opacity-50"
          >
            Ask
          </button>
        </div>
      </div>
    </main>
  );
}

"use client";

import { useState } from "react";
import ThemeToggle from "../components/ThemeToggle";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const COLORS = [
  "#8b5cf6",
  "#ec4899",
  "#3b82f6",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#14b8a6",
];

type ReportData = {
  topic: string;
  generated_sql: string;
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
  narrative: string;
};

async function downloadReportPdf(report: ReportData) {
  const res = await fetch(`${API_URL}/export/pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question: report.topic,
      columns: report.columns,
      rows: report.rows,
      narrative: report.narrative,
    }),
  });

  if (!res.ok) return;

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "askbase_report.pdf";
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export default function ReportPage() {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState<ReportData | null>(null);

  async function handleGenerate() {
    if (!topic.trim() || loading) return;

    const connectionRaw = sessionStorage.getItem("askbase_connection");
    if (!connectionRaw) {
      setError("No active connection. Please connect a database first.");
      return;
    }

    setLoading(true);
    setError("");
    setReport(null);

    try {
      const res = await fetch(`${API_URL}/report/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, connection: JSON.parse(connectionRaw) }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Report generation failed.");
      } else {
        setReport(data);
      }
    } catch {
      setError("Could not reach the backend.");
    } finally {
      setLoading(false);
    }
  }

  const chartReady =
    report && report.columns.length >= 2 && report.rows.length > 0;

  const categoryCol = report?.columns[0];
  const valueCol = report?.columns.find(
    (c) =>
      typeof report.rows[0][c] === "number" ||
      !isNaN(Number(report.rows[0][c])),
  );

  const barData =
    chartReady && categoryCol && valueCol
      ? report!.rows.slice(0, 15).map((row) => ({
          name: String(row[categoryCol]),
          value: Number(row[valueCol]),
        }))
      : [];

  return (
    <main
      className="min-h-screen px-6 py-10"
      style={{ backgroundColor: "var(--bg-app)", color: "var(--text-primary)" }}
    >
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-1">
          <h1 className="text-2xl font-bold">Generate a Report</h1>
          <ThemeToggle />
        </div>
        <p className="text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
          Describe what you want to analyze — e.g. &quot;sales by product and
          region&quot; — and AskBase will build charts and a written summary
          from your data.
        </p>

        <div className="flex gap-2 mb-8">
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
            placeholder="e.g. revenue by genre and country"
            className="flex-1 border rounded-xl px-4 py-3 text-sm"
            style={{
              backgroundColor: "var(--bg-surface)",
              borderColor: "var(--border-color)",
              color: "var(--text-primary)",
            }}
          />
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="bg-violet-500 hover:bg-violet-400 transition rounded-xl px-6 py-3 text-sm font-semibold disabled:opacity-50 text-white"
          >
            {loading ? "Generating..." : "Generate"}
          </button>
        </div>

        {error && (
          <p className="text-red-400 text-sm mb-6 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3">
            {error}
          </p>
        )}

        {loading && (
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            Analyzing your data — this involves two AI calls and may take a
            moment...
          </p>
        )}

        {report && (
          <div className="flex flex-col gap-8">
            <div>
              <h2 className="text-lg font-semibold mb-1">{report.topic}</h2>
              <p
                className="text-xs mb-4"
                style={{ color: "var(--text-secondary)" }}
              >
                {report.row_count} rows · generated from live data
              </p>
              <pre
                className="text-xs rounded-lg p-3 overflow-x-auto"
                style={{
                  backgroundColor: "var(--bg-surface)",
                  color: "var(--text-secondary)",
                }}
              >
                {report.generated_sql}
              </pre>
            </div>

            {barData.length > 0 && (
              <div className="flex flex-col gap-6">
                <div
                  className="border rounded-2xl p-6"
                  style={{
                    backgroundColor: "var(--bg-surface)",
                    borderColor: "var(--border-color)",
                  }}
                >
                  <p className="text-base font-semibold mb-4">Bar Chart</p>
                  <div style={{ width: "100%", height: 420 }}>
                    <ResponsiveContainer>
                      <BarChart data={barData}>
                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="var(--border-color)"
                        />
                        <XAxis
                          dataKey="name"
                          tick={{ fill: "var(--text-secondary)", fontSize: 10 }}
                        />
                        <YAxis
                          tick={{ fill: "var(--text-secondary)", fontSize: 10 }}
                        />
                        <Tooltip
                          contentStyle={{
                            background: "var(--bg-app)",
                            border: "1px solid var(--border-color)",
                          }}
                          labelStyle={{ color: "var(--text-primary)" }}
                        />
                        <Bar
                          dataKey="value"
                          fill="#8b5cf6"
                          radius={[4, 4, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div
                  className="border rounded-2xl p-6"
                  style={{
                    backgroundColor: "var(--bg-surface)",
                    borderColor: "var(--border-color)",
                  }}
                >
                  <p className="text-base font-semibold mb-4">Distribution</p>
                  <div style={{ width: "100%", height: 420 }}>
                    <ResponsiveContainer>
                      <PieChart>
                        <Pie
                          data={barData.slice(0, 8)}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          outerRadius={140}
                          label
                        >
                          {barData.slice(0, 8).map((_, i) => (
                            <Cell key={i} fill={COLORS[i % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{
                            background: "var(--bg-app)",
                            border: "1px solid var(--border-color)",
                          }}
                        />
                        <Legend
                          wrapperStyle={{
                            fontSize: 11,
                            color: "var(--text-secondary)",
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}

            <div
              className="border rounded-2xl p-6"
              style={{
                backgroundColor: "var(--bg-surface)",
                borderColor: "var(--border-color)",
              }}
            >
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium">Analysis</p>
                <button
                  onClick={() => downloadReportPdf(report)}
                  className="text-xs px-3 py-1.5 rounded-md bg-violet-500 hover:bg-violet-400 transition text-white"
                >
                  ⬇ Download PDF
                </button>
              </div>
              <div
                className="text-sm whitespace-pre-line leading-relaxed"
                style={{ color: "var(--text-secondary)" }}
              >
                {report.narrative}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

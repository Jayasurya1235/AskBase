"use client";

import { useEffect, useState } from "react";
import ThemeToggle from "../components/ThemeToggle";

type ColumnInfo = {
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
};

type ForeignKeyInfo = {
  column: string;
  references_table: string;
  references_column: string;
};

type TableInfo = {
  name: string;
  columns: ColumnInfo[];
  foreign_keys: ForeignKeyInfo[];
};

type SchemaResponse = {
  database: string;
  tables: TableInfo[];
};

export default function Dashboard() {
  const [schema, setSchema] = useState<SchemaResponse | null>(null);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("askbase_schema");
    if (stored) {
      const parsed: SchemaResponse = JSON.parse(stored);
      setSchema(parsed);
      if (parsed.tables.length > 0) {
        setSelectedTable(parsed.tables[0].name);
      }
    }
  }, []);

  if (!schema) {
    return (
      <main
        className="min-h-screen flex items-center justify-center px-6"
        style={{
          backgroundColor: "var(--bg-app)",
          color: "var(--text-primary)",
        }}
      >
        <p style={{ color: "var(--text-secondary)" }}>
          No schema data found — connect a database first from the home page.
        </p>
      </main>
    );
  }

  const activeTable = schema.tables.find((t) => t.name === selectedTable);

  return (
    <main
      className="min-h-screen flex flex-col"
      style={{ backgroundColor: "var(--bg-app)", color: "var(--text-primary)" }}
    >
      <header
        className="border-b px-6 py-4 flex items-center justify-between"
        style={{ borderColor: "var(--border-color)" }}
      >
        <span className="text-lg font-semibold">AskBase Dashboard</span>
        <ThemeToggle />
      </header>

      <div className="flex flex-1">
        <aside
          className="w-64 border-r p-5"
          style={{ borderColor: "var(--border-color)" }}
        >
          <p
            className="text-xs uppercase tracking-wide truncate mb-4"
            style={{ color: "var(--text-secondary)" }}
            title={`${schema.database} · ${schema.tables.length} tables`}
          >
            {schema.database.split("/").pop()} · {schema.tables.length} tables
          </p>

          <a
            href="/chat"
            className="block mb-2 text-center bg-violet-500 hover:bg-violet-400 transition rounded-lg py-2 text-sm font-semibold text-white"
          >
            Ask a question →
          </a>

          <a
            href="/report"
            className="block mb-4 text-center border hover:opacity-80 transition rounded-lg py-2 text-sm font-semibold"
            style={{
              backgroundColor: "var(--bg-surface)",
              borderColor: "var(--border-color)",
            }}
          >
            Generate Report →
          </a>

          <div className="flex flex-col gap-1">
            {schema.tables.map((table) => (
              <button
                key={table.name}
                onClick={() => setSelectedTable(table.name)}
                className={`text-left px-3 py-2 rounded-lg text-sm transition cursor-default ${
                  selectedTable === table.name ? "bg-gray-500 text-white" : ""
                }`}
                style={
                  selectedTable !== table.name
                    ? { color: "var(--text-secondary)" }
                    : undefined
                }
              >
                {table.name}
              </button>
            ))}
          </div>
        </aside>

        <section className="flex-1 p-8">
          {activeTable ? (
            <>
              <h1 className="text-2xl font-semibold mb-1">
                {activeTable.name}
              </h1>
              <p
                className="text-sm mb-6"
                style={{ color: "var(--text-secondary)" }}
              >
                {activeTable.columns.length} columns ·{" "}
                {activeTable.foreign_keys.length} relationships
              </p>

              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr
                    className="text-left border-b"
                    style={{
                      borderColor: "var(--border-color)",
                      color: "var(--text-secondary)",
                    }}
                  >
                    <th className="pb-2 pr-4">Column</th>
                    <th className="pb-2 pr-4">Type</th>
                    <th className="pb-2 pr-4">Nullable</th>
                    <th className="pb-2">Key</th>
                  </tr>
                </thead>
                <tbody>
                  {activeTable.columns.map((col) => (
                    <tr
                      key={col.name}
                      className="border-b"
                      style={{ borderColor: "var(--border-color)" }}
                    >
                      <td className="py-2 pr-4 font-medium">{col.name}</td>
                      <td
                        className="py-2 pr-4"
                        style={{ color: "var(--text-secondary)" }}
                      >
                        {col.type}
                      </td>
                      <td
                        className="py-2 pr-4"
                        style={{ color: "var(--text-secondary)" }}
                      >
                        {col.nullable ? "Yes" : "No"}
                      </td>
                      <td className="py-2">
                        {col.primary_key && (
                          <span className="text-xs bg-violet-500/20 text-violet-400 px-2 py-0.5 rounded">
                            PRIMARY
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {activeTable.foreign_keys.length > 0 && (
                <div className="mt-8">
                  <p
                    className="text-xs uppercase tracking-wide mb-2"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    Relationships
                  </p>
                  <div className="flex flex-col gap-1">
                    {activeTable.foreign_keys.map((fk, i) => (
                      <p
                        key={i}
                        className="text-sm"
                        style={{ color: "var(--text-secondary)" }}
                      >
                        <span style={{ color: "var(--text-primary)" }}>
                          {fk.column}
                        </span>{" "}
                        → {fk.references_table}.{fk.references_column}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <p style={{ color: "var(--text-secondary)" }}>
              Select a table to view its columns.
            </p>
          )}
        </section>
      </div>
    </main>
  );
}

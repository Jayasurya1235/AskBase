"use client";

import { useEffect, useState } from "react";

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
      <main className="min-h-screen bg-[#0b0d10] text-white flex items-center justify-center px-6">
        <p className="text-neutral-400">
          No schema data found — connect a database first from the home page.
        </p>
      </main>
    );
  }

  const activeTable = schema.tables.find((t) => t.name === selectedTable);

  return (
    <main className="min-h-screen bg-[#0b0d10] text-white flex">
      {/* Sidebar: table list */}
      <aside className="w-64 border-r border-white/10 p-5">
        <p className="text-xs text-neutral-500 uppercase tracking-wide mb-3">
          {schema.database} · {schema.tables.length} tables
        </p>
        <div className="flex flex-col gap-1">
          {schema.tables.map((table) => (
            <button
              key={table.name}
              onClick={() => setSelectedTable(table.name)}
              className={`text-left px-3 py-2 rounded-lg text-sm transition ${
                selectedTable === table.name
                  ? "bg-violet-500 text-white"
                  : "text-neutral-400 hover:bg-white/5"
              }`}
            >
              {table.name}
            </button>
          ))}
        </div>
      </aside>

      {/* Main: selected table's columns */}
      <section className="flex-1 p-8">
        {activeTable ? (
          <>
            <h1 className="text-2xl font-semibold mb-1">{activeTable.name}</h1>
            <p className="text-neutral-500 text-sm mb-6">
              {activeTable.columns.length} columns ·{" "}
              {activeTable.foreign_keys.length} relationships
            </p>

            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="text-left text-neutral-500 border-b border-white/10">
                  <th className="pb-2 pr-4">Column</th>
                  <th className="pb-2 pr-4">Type</th>
                  <th className="pb-2 pr-4">Nullable</th>
                  <th className="pb-2">Key</th>
                </tr>
              </thead>
              <tbody>
                {activeTable.columns.map((col) => (
                  <tr key={col.name} className="border-b border-white/5">
                    <td className="py-2 pr-4 font-medium">{col.name}</td>
                    <td className="py-2 pr-4 text-neutral-400">{col.type}</td>
                    <td className="py-2 pr-4 text-neutral-400">
                      {col.nullable ? "Yes" : "No"}
                    </td>
                    <td className="py-2">
                      {col.primary_key && (
                        <span className="text-xs bg-violet-500/20 text-violet-300 px-2 py-0.5 rounded">
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
                <p className="text-xs text-neutral-500 uppercase tracking-wide mb-2">
                  Relationships
                </p>
                <div className="flex flex-col gap-1">
                  {activeTable.foreign_keys.map((fk, i) => (
                    <p key={i} className="text-sm text-neutral-400">
                      <span className="text-white">{fk.column}</span> →{" "}
                      {fk.references_table}.{fk.references_column}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <p className="text-neutral-500">
            Select a table to view its columns.
          </p>
        )}
      </section>
    </main>
  );
}

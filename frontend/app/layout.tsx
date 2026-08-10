import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AskBase",
  description: "Ask your database a question. Get a report back.",
};

// Runs before React hydrates, directly in the HTML — this prevents a
// "flash" of the wrong theme on page load, since it sets the class
// on <html> immediately rather than waiting for a React effect.
const themeInitScript = `
  (function() {
    try {
      var saved = localStorage.getItem('askbase_theme');
      var prefersDark = saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
      if (prefersDark) document.documentElement.classList.add('dark');
    } catch (e) {}
  })();
`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}

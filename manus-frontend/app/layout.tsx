import type { Metadata } from "next";
import "./globals.css";


export const metadata: Metadata = {
  title: "Manus Clone",
  description: "manus clone",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className="font-sans antialiased"
        style={{
          fontFamily: "var(--font-sans)",
        }}
        suppressHydrationWarning={true}
      >
        {children}
      </body>
    </html>
  );
}


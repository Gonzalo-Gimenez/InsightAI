import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InsightAI",
  description: "Analizá tus ventas con IA y datos reales en 3D",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}

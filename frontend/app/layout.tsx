import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NOVA · Core",
  description: "Persistent task continuity across simulated device contexts. Local Phase 1 foundation.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

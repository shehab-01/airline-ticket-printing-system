import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { CircleUser, Menu } from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Airline Ticket System",
  description: "Ticket printing management UI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50`}>
        <div className="min-h-screen flex flex-col font-sans">
          <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4"></div>
            <div>
              <CircleUser className="h-8 w-8 text-gray-400" />
            </div>
          </header>

          {/* Main Content Area */}
          <main className="flex-1 p-8 max-w-7xl mx-auto w-full">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

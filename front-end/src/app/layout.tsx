import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import Image from "next/image";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Fable Flux - AI-Powered Bedtime Stories",
  description:
    "Create magical personalized bedtime stories with the power of AI. Tell us what you'd like your story to be about, and our AI storyteller will craft a unique tale just for you.",
  keywords:
    "bedtime stories, AI stories, children stories, personalized stories, story generator",
  authors: [{ name: "Fable Flux" }],
  openGraph: {
    title: "Fable Flux - AI-Powered Bedtime Stories",
    description:
      "Create magical personalized bedtime stories with the power of AI",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}

        {/* Fixed OpenAI Logo */}
        <Link
          href="/technical-details"
          className="fixed bottom-4 right-4 z-50 hover:scale-110 transition-transform duration-200"
        >
          <Image
            src="/openai.png"
            alt="Technical Details - Powered by OpenAI"
            width={48}
            height={48}
            className="drop-shadow-lg"
          />
        </Link>
      </body>
    </html>
  );
}

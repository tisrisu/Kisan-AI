import "./globals.css";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import { LanguageProvider } from "@/lib/LanguageProvider";

export const metadata = {
  title: "KisanAI — AI-Powered Crop Disease Diagnosis",
  description:
    "Upload a leaf photo and get instant AI-powered disease diagnosis with treatment recommendations. Multi-modal fusion AI that learns your district's fields.",
  keywords: "crop disease, AI diagnosis, agriculture, farming, India, KisanAI",
  openGraph: {
    title: "KisanAI — AI-Powered Crop Disease Diagnosis",
    description: "Smart crop care for Indian farmers",
    type: "website",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#050d09" />
        <link rel="manifest" href="/manifest.json" />
      </head>
      <body>
        <LanguageProvider>
          <Navbar />
          <main className="main-content">{children}</main>
          <Footer />
        </LanguageProvider>
      </body>
    </html>
  );
}

"use client";

/**
 * KisanAI — History Page
 * Shows past diagnoses timeline.
 * Uses i18n for multilingual support.
 */

import { useState } from "react";
import { useLanguage } from "@/lib/LanguageProvider";
import { RevealSection } from "@/lib/animations";

const DEMO_HISTORY = [
  {
    id: 1, disease_name: "Rice Blast", confidence: 94.2, severity: "Moderate",
    crop: "IR-64 (Rice)", district: "Guntur, AP", season: "Kharif",
    date: "2024-12-10T10:30:00", feedback: true,
  },
  {
    id: 2, disease_name: "Brown Spot", confidence: 87.5, severity: "Mild",
    crop: "Samba Mahsuri (Rice)", district: "Krishna, AP", season: "Kharif",
    date: "2024-12-08T14:15:00", feedback: true,
  },
  {
    id: 3, disease_name: "Leaf Curl Virus", confidence: 91.3, severity: "Severe",
    crop: "Teja (Chili)", district: "Guntur, AP", season: "Rabi",
    date: "2024-12-05T09:00:00", feedback: false,
  },
  {
    id: 4, disease_name: "Late Blight", confidence: 88.7, severity: "Moderate",
    crop: "Kufri Jyoti (Potato)", district: "Ludhiana, PB", season: "Rabi",
    date: "2024-12-01T16:45:00", feedback: false,
  },
  {
    id: 5, disease_name: "Healthy", confidence: 96.1, severity: "Mild",
    crop: "HD-2967 (Wheat)", district: "Lucknow, UP", season: "Rabi",
    date: "2024-11-28T11:20:00", feedback: true,
  },
];

export default function HistoryPage() {
  const { t } = useLanguage();
  const [filter, setFilter] = useState("all");

  const filtered = filter === "all" ? DEMO_HISTORY :
    filter === "pending" ? DEMO_HISTORY.filter(h => !h.feedback) :
    DEMO_HISTORY.filter(h => h.feedback);

  const severityColor = (s) => {
    if (s === "Mild") return "var(--accent-green)";
    if (s === "Moderate") return "var(--accent-orange)";
    return "var(--accent-coral)";
  };

  return (
    <div className="container" style={{ padding: "var(--space-3xl) var(--space-xl)" }}>
      <div className="animate-in">
        <div className="section-label">📋 {t("history_label")}</div>
        <h1 className="section-title">{t("history_title")}</h1>
        <p className="section-subtitle" style={{ marginBottom: "var(--space-xl)" }}>
          Review your previous crop diagnoses and provide feedback
        </p>
      </div>

      {/* Filters */}
      <div style={{ display: "flex", gap: "var(--space-sm)", marginBottom: "var(--space-xl)" }}>
        {[
          { value: "all", label: "All" },
          { value: "pending", label: "Pending Feedback" },
          { value: "reviewed", label: "Reviewed" },
        ].map((f) => (
          <button
            key={f.value}
            className={`btn ${filter === f.value ? "btn-primary" : "btn-ghost"} btn-sm`}
            onClick={() => setFilter(f.value)}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* History List */}
      <div className="history-timeline">
        {filtered.map((item, idx) => (
          <RevealSection key={item.id} delay={idx * 80}>
            <div className="card card-shimmer history-item">
              <div
                className="history-thumb"
                style={{
                  background: "var(--bg-elevated)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 32,
                }}
              >
                🌿
              </div>

              <div className="history-info">
                <h3 style={{ display: "flex", alignItems: "center", gap: "var(--space-sm)", flexWrap: "wrap" }}>
                  {item.disease_name}
                  <span
                    className="badge"
                    style={{
                      background: `${severityColor(item.severity)}22`,
                      color: severityColor(item.severity),
                    }}
                  >
                    {item.severity}
                  </span>
                </h3>
                <div className="history-meta">
                  <span>🌾 {item.crop}</span>
                  <span>📍 {item.district}</span>
                  <span>🗓️ {item.season}</span>
                  <span style={{ fontFamily: "var(--font-mono)" }}>
                    {item.confidence}%
                  </span>
                </div>
              </div>

              <div style={{ textAlign: "right" }}>
                <p style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)", marginBottom: "var(--space-sm)" }}>
                  {new Date(item.date).toLocaleDateString("en-IN", {
                    day: "numeric", month: "short", year: "numeric",
                  })}
                </p>
                {item.feedback ? (
                  <span className="badge badge-green">✓ Reviewed</span>
                ) : (
                  <button className="btn btn-secondary btn-sm">Give Feedback</button>
                )}
              </div>
            </div>
          </RevealSection>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="card" style={{ textAlign: "center", padding: "var(--space-3xl)" }}>
          <div style={{ fontSize: 48, marginBottom: "var(--space-md)" }}>🌱</div>
          <h3 style={{ marginBottom: "var(--space-sm)" }}>{t("no_history") || "No diagnoses yet"}</h3>
          <p style={{ color: "var(--text-tertiary)", marginBottom: "var(--space-lg)" }}>
            Upload your first leaf photo to get started!
          </p>
          <a href="/diagnose" className="btn btn-primary">Start Diagnosis</a>
        </div>
      )}
    </div>
  );
}

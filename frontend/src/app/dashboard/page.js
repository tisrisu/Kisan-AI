"use client";

/**
 * KisanAI — Dashboard Page
 * District-level statistics and platform metrics.
 * Uses animated counters and scroll-reveal.
 */

import { useLanguage } from "@/lib/LanguageProvider";
import { RevealSection, useAnimatedCounter } from "@/lib/animations";

function DashStat({ icon, value, label, color }) {
  const { containerRef, countRef } = useAnimatedCounter(value);
  return (
    <div className="card card-shimmer stat-card" ref={containerRef}>
      <div style={{ fontSize: 32, marginBottom: "var(--space-sm)" }}>{icon}</div>
      <div className={`stat-value ${color}`} ref={countRef}>0</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export default function DashboardPage() {
  const { t } = useLanguage();

  const stats = [
    { label: t("total_diagnoses") || "Total Diagnoses", value: "12847", color: "stat-value-green", icon: "🔬" },
    { label: t("active_districts") || "Active Districts", value: "30", color: "stat-value-cyan", icon: "📍" },
    { label: t("model_accuracy") || "Model Accuracy", value: "94.2%", color: "stat-value-orange", icon: "🎯" },
    { label: t("verified_feedback") || "Verified Feedback", value: "4521", color: "stat-value-purple", icon: "✅" },
  ];

  const topDiseases = [
    { name: "Rice Blast", count: 2340, percentage: 18.2 },
    { name: "Brown Spot", count: 1856, percentage: 14.4 },
    { name: "Late Blight", count: 1623, percentage: 12.6 },
    { name: "Leaf Curl Virus", count: 1245, percentage: 9.7 },
    { name: "Bacterial Leaf Blight", count: 987, percentage: 7.7 },
  ];

  const activeDistricts = [
    { name: "Guntur", state: "AP", submissions: 834, model: true, accuracy: 96.1 },
    { name: "Thanjavur", state: "TN", submissions: 612, model: true, accuracy: 95.3 },
    { name: "Ludhiana", state: "PB", submissions: 523, model: true, accuracy: 94.8 },
    { name: "Krishna", state: "AP", submissions: 445, model: false, accuracy: 93.2 },
    { name: "Karimnagar", state: "TS", submissions: 387, model: false, accuracy: 92.7 },
    { name: "Nashik", state: "MH", submissions: 298, model: false, accuracy: 91.5 },
    { name: "Coimbatore", state: "TN", submissions: 156, model: false, accuracy: 90.8 },
    { name: "Lucknow", state: "UP", submissions: 89, model: false, accuracy: 89.2 },
  ];

  const barColors = ["var(--accent-coral)", "var(--accent-orange)", "var(--accent-gold)", "var(--accent-green)", "var(--accent-cyan)"];

  return (
    <div className="container" style={{ padding: "var(--space-3xl) var(--space-xl)" }}>
      <div className="animate-in">
        <div className="section-label">📊 {t("dash_label")}</div>
        <h1 className="section-title">{t("dash_title")}</h1>
        <p className="section-subtitle" style={{ marginBottom: "var(--space-2xl)" }}>
          Real-time metrics across all districts and models
        </p>
      </div>

      {/* Stats Grid — Animated Counters */}
      <div className="stats-grid">
        {stats.map((stat, idx) => (
          <DashStat key={idx} {...stat} />
        ))}
      </div>

      {/* Two column layout */}
      <div className="dashboard-two-col" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-lg)" }}>
        {/* Top Diseases */}
        <RevealSection delay={100}>
          <div className="card card-shimmer">
            <div className="badge badge-coral" style={{ marginBottom: "var(--space-lg)" }}>
              🦠 TOP DISEASES DETECTED
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-md)" }}>
              {topDiseases.map((disease, idx) => (
                <div key={idx}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontSize: "var(--font-size-sm)", fontWeight: 600 }}>{disease.name}</span>
                    <span style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                      {disease.count.toLocaleString()} ({disease.percentage}%)
                    </span>
                  </div>
                  <div style={{ height: 6, borderRadius: "var(--radius-full)", background: "var(--bg-primary)", overflow: "hidden" }}>
                    <div
                      className="reveal-on-scroll"
                      style={{
                        height: "100%",
                        width: `${disease.percentage * 5}%`,
                        borderRadius: "var(--radius-full)",
                        background: barColors[idx] || "var(--accent-green)",
                        transition: "width 1.2s cubic-bezier(0.16, 1, 0.3, 1)",
                        transitionDelay: `${idx * 150}ms`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </RevealSection>

        {/* Active Districts */}
        <RevealSection delay={200}>
          <div className="card card-shimmer">
            <div className="badge badge-green" style={{ marginBottom: "var(--space-lg)" }}>
              📍 DISTRICT ACTIVITY
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-sm)" }}>
              {/* Table header */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 80px 80px 80px", gap: "var(--space-sm)", paddingBottom: "var(--space-sm)", borderBottom: "1px solid var(--border-primary)" }}>
                <span style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: 1 }}>District</span>
                <span style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, textAlign: "right" }}>Subs</span>
                <span style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, textAlign: "right" }}>Acc%</span>
                <span style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, textAlign: "right" }}>Model</span>
              </div>
              {activeDistricts.map((dist, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 80px 80px 80px",
                    gap: "var(--space-sm)",
                    padding: "var(--space-sm) 0",
                    borderBottom: "1px solid var(--border-subtle)",
                    alignItems: "center",
                  }}
                >
                  <div>
                    <span style={{ fontSize: "var(--font-size-sm)", fontWeight: 600 }}>{dist.name}</span>
                    <span style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)", marginLeft: 6 }}>{dist.state}</span>
                  </div>
                  <span style={{ fontSize: "var(--font-size-sm)", fontFamily: "var(--font-mono)", textAlign: "right", color: "var(--text-secondary)" }}>
                    {dist.submissions}
                  </span>
                  <span style={{ fontSize: "var(--font-size-sm)", fontFamily: "var(--font-mono)", textAlign: "right", color: "var(--accent-green)" }}>
                    {dist.accuracy}%
                  </span>
                  <span style={{ textAlign: "right" }}>
                    {dist.model ? (
                      <span className="badge badge-green">Custom</span>
                    ) : (
                      <span className="badge" style={{ background: "var(--bg-primary)", color: "var(--text-muted)" }}>Base</span>
                    )}
                  </span>
                </div>
              ))}
            </div>

            {/* Fine-tuning threshold */}
            <div style={{ marginTop: "var(--space-lg)", padding: "var(--space-md)", background: "var(--bg-secondary)", borderRadius: "var(--radius-md)", fontSize: "var(--font-size-xs)", color: "var(--text-tertiary)", display: "flex", alignItems: "center", gap: "var(--space-sm)" }}>
              <span style={{ color: "var(--accent-gold)" }}>⚡</span>
              Districts with 50+ verified submissions automatically get a fine-tuned model
            </div>
          </div>
        </RevealSection>
      </div>

      {/* Pipeline Status */}
      <RevealSection delay={300}>
        <div className="card card-shimmer" style={{ marginTop: "var(--space-lg)" }}>
          <div className="badge badge-purple" style={{ marginBottom: "var(--space-lg)" }}>
            🔄 MODEL PIPELINE
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "var(--space-lg)", textAlign: "center" }}>
            {[
              { icon: "📱", label: "Frontend", desc: "PWA Web App", status: "active" },
              { icon: "⚡", label: "API Layer", desc: "FastAPI Server", status: "active" },
              { icon: "🧠", label: "ML Engine", desc: "Multi-Modal Classifier", status: "active" },
              { icon: "💾", label: "Data Layer", desc: "PostgreSQL + MinIO", status: "active" },
              { icon: "🔄", label: "Pipeline", desc: "Auto Fine-Tuning", status: "ready" },
            ].map((item, idx) => (
              <div key={idx}>
                <div style={{ fontSize: 28, marginBottom: "var(--space-sm)" }}>{item.icon}</div>
                <div style={{ fontSize: "var(--font-size-sm)", fontWeight: 700, color: "var(--accent-green)", marginBottom: 2 }}>{item.label}</div>
                <div style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)" }}>{item.desc}</div>
                <div className={`badge ${item.status === "active" ? "badge-green" : "badge-orange"}`} style={{ marginTop: "var(--space-sm)" }}>
                  {item.status === "active" ? "● Active" : "◌ Ready"}
                </div>
              </div>
            ))}
          </div>
        </div>
      </RevealSection>
    </div>
  );
}

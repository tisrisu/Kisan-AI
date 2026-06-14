"use client";

/**
 * KisanAI — Home / Landing Page
 * Premium dark theme with animated hero, feature flow, problem section, and stats.
 * Uses i18n for multilingual support and scroll-reveal animations.
 */

import { useLanguage } from "@/lib/LanguageProvider";
import { RevealSection, useAnimatedCounter } from "@/lib/animations";

/* ─── Animated Stat Counter ─── */
function AnimatedStat({ value, label }) {
  const { containerRef, countRef } = useAnimatedCounter(value);
  return (
    <div className="hero-stat" ref={containerRef}>
      <div className="hero-stat-value" ref={countRef}>0</div>
      <div className="hero-stat-label">{label}</div>
    </div>
  );
}

export default function HomePage() {
  const { t } = useLanguage();

  return (
    <>
      {/* ═══════ HERO SECTION ═══════ */}
      <section className="hero" id="hero">
        <div className="hero-bg" />
        <div className="hero-glow hero-glow-1" />
        <div className="hero-glow hero-glow-2" />

        {/* Floating particles */}
        <div className="particles" suppressHydrationWarning>
          {Array.from({ length: 20 }).map((_, i) => (
            <div
              key={i}
              className="particle"
              suppressHydrationWarning
              style={{
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 15}s`,
                animationDuration: `${10 + Math.random() * 10}s`,
                width: `${2 + Math.random() * 4}px`,
                height: `${2 + Math.random() * 4}px`,
                opacity: 0.1 + Math.random() * 0.3,
              }}
            />
          ))}
        </div>

        <div className="container">
          <div className="hero-content animate-in">
            <div className="section-label">
              🌱 {t("hero_label")}
            </div>

            <h1 className="hero-title">
              {t("hero_title_1")}{" "}
              <span className="gradient-text-animated">{t("hero_title_2")}</span>
            </h1>

            <p className="hero-description">
              {t("hero_desc")}
            </p>

            <div className="hero-actions">
              <a href="/diagnose" className="btn btn-primary btn-lg glow-pulse">
                🔬 {t("hero_cta")}
              </a>
              <a href="#how-it-works" className="btn btn-secondary btn-lg">
                {t("hero_cta_2")} →
              </a>
            </div>

            <div className="hero-stats">
              <AnimatedStat value="54K+" label={t("stat_diagnoses") || "Training Images"} />
              <AnimatedStat value="30+" label={t("stat_districts") || "Districts"} />
              <AnimatedStat value="94%" label={t("stat_accuracy") || "Accuracy"} />
              <AnimatedStat value="4" label={t("stat_languages") || "Languages"} />
            </div>
          </div>
        </div>
      </section>

      {/* ═══════ PROBLEM SECTION ═══════ */}
      <section className="page-section" style={{ background: "var(--bg-secondary)" }} id="problem">
        <div className="container">
          <RevealSection>
            <div className="section-label" style={{ background: "var(--accent-coral-dim)", borderColor: "rgba(255,107,107,0.2)", color: "var(--accent-coral)" }}>
              ⚠️ THE PROBLEM
            </div>
            <h2 className="section-title">Why Do Global Disease Models Fail Our Farmers?</h2>
            <p className="section-subtitle" style={{ marginBottom: "var(--space-2xl)" }}>
              India loses ~₹50,000 Cr annually to crop diseases • 70% of farmers lack access to expert diagnosis
            </p>
          </RevealSection>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "var(--space-lg)" }}>
            <RevealSection delay={100}>
              <div className="card card-accent-coral card-shimmer">
                <div className="badge badge-coral" style={{ marginBottom: "var(--space-md)" }}>01</div>
                <h3 style={{ color: "var(--accent-coral)", fontSize: "var(--font-size-lg)", marginBottom: "var(--space-sm)" }}>Lab vs Field Gap</h3>
                <p style={{ color: "var(--text-tertiary)", fontSize: "var(--font-size-sm)", lineHeight: 1.7 }}>
                  Training data comes from controlled labs with perfect lighting. Real fields have shadows, dirt, overlapping leaves, and low-quality phone cameras.
                </p>
              </div>
            </RevealSection>

            <RevealSection delay={200}>
              <div className="card card-accent-orange card-shimmer">
                <div className="badge badge-orange" style={{ marginBottom: "var(--space-md)" }}>02</div>
                <h3 style={{ color: "var(--accent-orange)", fontSize: "var(--font-size-lg)", marginBottom: "var(--space-sm)" }}>Regional Blindness</h3>
                <p style={{ color: "var(--text-tertiary)", fontSize: "var(--font-size-sm)", lineHeight: 1.7 }}>
                  A model trained on American corn diseases has never seen Indian Basmati rice varieties. Local disease strains are invisible to generic models.
                </p>
              </div>
            </RevealSection>

            <RevealSection delay={300}>
              <div className="card card-accent-purple card-shimmer">
                <div className="badge badge-purple" style={{ marginBottom: "var(--space-md)" }}>03</div>
                <h3 style={{ color: "var(--accent-purple)", fontSize: "var(--font-size-lg)", marginBottom: "var(--space-sm)" }}>No Vernacular Support</h3>
                <p style={{ color: "var(--text-tertiary)", fontSize: "var(--font-size-sm)", lineHeight: 1.7 }}>
                  Farmers describe symptoms in Hindi, Tamil, Telugu — not English scientific terms. Existing tools ignore this rich contextual information.
                </p>
              </div>
            </RevealSection>

            <RevealSection delay={400}>
              <div className="card card-accent-cyan card-shimmer">
                <div className="badge badge-green" style={{ marginBottom: "var(--space-md)" }}>04</div>
                <h3 style={{ color: "var(--accent-cyan)", fontSize: "var(--font-size-lg)", marginBottom: "var(--space-sm)" }}>One-Size-Fits-None</h3>
                <p style={{ color: "var(--text-tertiary)", fontSize: "var(--font-size-sm)", lineHeight: 1.7 }}>
                  A single global model serves all districts identically. But Guntur (AP) grows chilies, Thanjavur (TN) grows rice — they need different expertise.
                </p>
              </div>
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══════ HOW IT WORKS ═══════ */}
      <section className="page-section" id="how-it-works">
        <div className="container">
          <RevealSection>
            <div className="section-label">🔄 {t("flow_label") || "HOW IT WORKS"}</div>
            <h2 className="section-title">{t("flow_title") || "Four Steps to Healthy Crops"}</h2>
            <p className="section-subtitle">
              From leaf photo to treatment recommendation in under 10 seconds
            </p>
          </RevealSection>

          <div className="flow-grid">
            <RevealSection delay={100}>
              <div className="card flow-card card-shimmer">
                <div className="flow-icon flow-icon-upload">📸</div>
                <h3 className="flow-title">{t("upload")}</h3>
                <p className="flow-desc">{t("upload_desc")}</p>
              </div>
            </RevealSection>

            <RevealSection delay={200}>
              <div className="card flow-card card-shimmer">
                <div className="flow-icon flow-icon-diagnose">🔬</div>
                <h3 className="flow-title">{t("diagnose")}</h3>
                <p className="flow-desc">{t("diagnose_desc")}</p>
              </div>
            </RevealSection>

            <RevealSection delay={300}>
              <div className="card flow-card card-shimmer">
                <div className="flow-icon flow-icon-treat">💊</div>
                <h3 className="flow-title">{t("treat")}</h3>
                <p className="flow-desc">{t("treat_desc")}</p>
              </div>
            </RevealSection>

            <RevealSection delay={400}>
              <div className="card flow-card card-shimmer">
                <div className="flow-icon flow-icon-adapt">🧠</div>
                <h3 className="flow-title">{t("adapt")}</h3>
                <p className="flow-desc">{t("adapt_desc")}</p>
              </div>
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══════ KEY INNOVATION ═══════ */}
      <section className="page-section" style={{ background: "var(--bg-secondary)" }}>
        <div className="container">
          <RevealSection>
            <div className="card card-glass glow-pulse" style={{ borderColor: "var(--accent-green)", padding: "var(--space-2xl)", maxWidth: 800 }}>
              <div className="badge badge-green" style={{ marginBottom: "var(--space-md)", fontSize: "var(--font-size-xs)" }}>
                ✨ KEY INNOVATION
              </div>
              <h3 style={{ fontSize: "var(--font-size-xl)", fontWeight: 700, marginBottom: "var(--space-md)" }}>
                Per-District Fine-Tuning
              </h3>
              <p style={{ color: "var(--text-tertiary)", lineHeight: 1.8 }}>
                When a district collects <strong style={{ color: "var(--accent-green)" }}>50+ verified farmer submissions</strong>,
                the base model automatically fine-tunes on local data. Even 50-200 local images dramatically
                improve accuracy because the base model already understands leaf disease features — it just
                needs to learn the local variations in crop varieties, lighting, and disease strains.
              </p>
            </div>
          </RevealSection>
        </div>
      </section>

      {/* ═══════ TECH ARCHITECTURE ═══════ */}
      <section className="page-section" id="architecture">
        <div className="container">
          <RevealSection>
            <div className="section-label">🏗️ ARCHITECTURE</div>
            <h2 className="section-title">Multi-Modal Fusion AI</h2>
            <p className="section-subtitle" style={{ marginBottom: "var(--space-2xl)" }}>
              Three neural network branches fused into one powerful classifier
            </p>
          </RevealSection>

          <div className="arch-grid" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "var(--space-lg)" }}>
            <RevealSection delay={100}>
              <div className="card card-accent-green card-shimmer">
                <div className="badge badge-green" style={{ marginBottom: "var(--space-md)" }}>📸 IMAGE BRANCH</div>
                <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "var(--space-sm)" }}>
                  <li style={{ color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>Input: Leaf Photo (380×380×3)</li>
                  <li style={{ color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>EfficientNet-B4 (ImageNet pretrained)</li>
                  <li style={{ color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>GlobalAveragePooling2D</li>
                  <li style={{ color: "var(--accent-green)", fontSize: "var(--font-size-sm)", fontWeight: 600 }}>Output: 1792-dim image embedding</li>
                </ul>
              </div>
            </RevealSection>

            <RevealSection delay={200}>
              <div className="card card-accent-orange card-shimmer">
                <div className="badge badge-orange" style={{ marginBottom: "var(--space-md)" }}>📝 TEXT BRANCH</div>
                <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "var(--space-sm)" }}>
                  <li style={{ color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>Input: Symptom Description</li>
                  <li style={{ color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>Multilingual BERT Encoder</li>
                  <li style={{ color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>Sentence Embedding Layer</li>
                  <li style={{ color: "var(--accent-orange)", fontSize: "var(--font-size-sm)", fontWeight: 600 }}>Output: 256-dim text embedding</li>
                </ul>
              </div>
            </RevealSection>

            <RevealSection delay={300}>
              <div className="card card-accent-purple card-shimmer">
                <div className="badge badge-purple" style={{ marginBottom: "var(--space-md)" }}>🔑 CONTEXT BRANCH</div>
                <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "var(--space-sm)" }}>
                  <li style={{ color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>Input: District + Season + Crop</li>
                  <li style={{ color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>Categorical Embedding Layers</li>
                  <li style={{ color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>Concatenation</li>
                  <li style={{ color: "var(--accent-purple)", fontSize: "var(--font-size-sm)", fontWeight: 600 }}>Output: 64-dim context embedding</li>
                </ul>
              </div>
            </RevealSection>
          </div>

          <RevealSection delay={400}>
            <div className="card card-glass" style={{ marginTop: "var(--space-lg)", borderColor: "var(--accent-cyan)", textAlign: "center", padding: "var(--space-2xl)" }}>
              <div className="badge badge-green" style={{ marginBottom: "var(--space-md)" }}>⚡ FUSION + CLASSIFICATION</div>
              <p style={{ color: "var(--text-secondary)", fontFamily: "var(--font-mono)", fontSize: "var(--font-size-sm)" }}>
                Concatenation → (1792 + 256 + 64) = <strong style={{ color: "var(--accent-green)" }}>2112-dim</strong> combined vector →
                Dense(512) → BatchNorm → Dropout(0.3) → Dense(256) → BatchNorm → Dropout(0.2)
              </p>
              <p style={{ color: "var(--accent-gold)", fontWeight: 700, marginTop: "var(--space-md)" }}>
                Two output heads: Disease Classification (softmax) + Severity Grading (3-class softmax)
              </p>
            </div>
          </RevealSection>
        </div>
      </section>

      {/* ═══════ CTA ═══════ */}
      <section className="page-section" style={{ background: "var(--bg-secondary)", textAlign: "center" }}>
        <div className="container">
          <RevealSection>
            <h2 className="section-title">Ready to Diagnose Your Crop?</h2>
            <p className="section-subtitle" style={{ margin: "0 auto var(--space-2xl)" }}>
              Upload a leaf photo and get instant AI-powered diagnosis with treatment recommendations.
            </p>
            <a href="/diagnose" className="btn btn-primary btn-lg glow-pulse">
              🔬 Start Free Diagnosis
            </a>
          </RevealSection>
        </div>
      </section>
    </>
  );
}

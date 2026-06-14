"use client";

/**
 * KisanAI — Results Page
 * Displays disease diagnosis, medications, precautions, severity, and feedback.
 * Uses i18n for multilingual support.
 */

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { DEMO_RESULT } from "@/lib/api";
import { useLanguage } from "@/lib/LanguageProvider";
import { RevealSection } from "@/lib/animations";

export default function ResultsPage() {
  const params = useParams();
  const { t, lang } = useLanguage();
  const [result, setResult] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [feedbackType, setFeedbackType] = useState(null);

  useEffect(() => {
    // Load result from session storage
    const stored = sessionStorage.getItem("diagnosis_result");
    const storedImage = sessionStorage.getItem("uploaded_image");

    if (stored) {
      setResult(JSON.parse(stored));
    } else {
      setResult(DEMO_RESULT);
    }

    if (storedImage) {
      setUploadedImage(storedImage);
    }
  }, []);

  const handleFeedback = async (isCorrect) => {
    setFeedbackGiven(true);
    setFeedbackType(isCorrect ? "correct" : "incorrect");
    // In production, this would call the API
  };

  if (!result) {
    return (
      <div className="container" style={{ padding: "var(--space-3xl) var(--space-xl)" }}>
        <div className="loading-spinner">
          <div className="spinner" />
          <p className="loading-text">Loading results...</p>
        </div>
      </div>
    );
  }

  const severity = result.severity;
  const severityClass = severity.level.toLowerCase();
  const severityPercent =
    severityClass === "mild" ? 33 :
    severityClass === "moderate" ? 66 : 100;

  // Get translated disease name if available
  const diseaseName = (result.translations && result.translations[lang])
    ? result.translations[lang]
    : result.disease_name;

  return (
    <div className="container" style={{ padding: "var(--space-3xl) var(--space-xl)" }}>
      {/* Header */}
      <div className="animate-in" style={{ marginBottom: "var(--space-2xl)" }}>
        <div className="section-label" style={{ background: "var(--accent-coral-dim)", borderColor: "rgba(255,107,107,0.2)", color: "var(--accent-coral)" }}>
          📋 {t("result_label")}
        </div>
        <h1 className="section-title">{t("result_title")}</h1>
      </div>

      {/* Results Grid */}
      <div className="results-grid animate-in animate-delay-1">
        {/* Disease Identified Card */}
        <div className="card card-shimmer result-disease-card" style={{ borderColor: "var(--accent-coral)" }}>
          <div className="badge badge-coral" style={{ marginBottom: "var(--space-lg)" }}>
            🔍 {t("disease_identified")}
          </div>

          {uploadedImage && (
            <img
              src={uploadedImage}
              alt="Uploaded leaf"
              style={{
                width: "100%",
                height: 180,
                objectFit: "cover",
                borderRadius: "var(--radius-md)",
                marginBottom: "var(--space-lg)",
                border: "1px solid var(--border-primary)",
              }}
            />
          )}

          <h2 className="result-disease-name">{diseaseName}</h2>
          <p className="result-scientific">{result.scientific_name}</p>

          <div style={{ marginBottom: "var(--space-lg)" }}>
            <span className="result-confidence-label">{t("confidence")}</span>
            <div className="result-confidence">{result.confidence}%</div>
          </div>

          {/* Severity Meter */}
          <div className="severity-meter">
            <div className="severity-label">{t("severity")}</div>
            <div className="severity-bar">
              <div
                className={`severity-fill ${severityClass}`}
                style={{ width: `${severityPercent}%` }}
              />
            </div>
            <div className={`severity-value ${severityClass}`}>
              {"■".repeat(Math.round(severityPercent / 10))}{"□".repeat(10 - Math.round(severityPercent / 10))} {severity.level.toUpperCase()}
            </div>
          </div>

          {/* Top 3 Predictions */}
          <div style={{ marginTop: "var(--space-lg)", paddingTop: "var(--space-md)", borderTop: "1px solid var(--border-primary)" }}>
            <p style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)", marginBottom: "var(--space-sm)", textTransform: "uppercase", letterSpacing: 1 }}>
              Other possibilities
            </p>
            {result.predictions?.slice(1).map((pred) => (
              <div
                key={pred.rank}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "6px 0",
                  fontSize: "var(--font-size-sm)",
                  color: "var(--text-tertiary)",
                }}
              >
                <span>{pred.disease_name}</span>
                <span style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
                  {pred.confidence}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recommended Medications Card */}
        <div className="card card-shimmer" style={{ borderColor: "var(--accent-green)" }}>
          <div className="badge badge-green" style={{ marginBottom: "var(--space-lg)" }}>
            💊 {t("recommended_meds")}
          </div>

          <div className="medication-list">
            {result.medications?.map((med, idx) => (
              <div className="medication-item" key={idx}>
                <div className="medication-name">{med.name}</div>
                <div className="medication-dosage">@ {med.dosage}</div>
                {med.application && (
                  <p style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)", marginTop: 4 }}>
                    {med.application}
                  </p>
                )}
              </div>
            ))}
          </div>

          {/* Prevention tips */}
          {result.prevention_tips?.length > 0 && (
            <div style={{ marginTop: "var(--space-xl)", paddingTop: "var(--space-md)", borderTop: "1px solid var(--border-primary)" }}>
              <p style={{ fontSize: "var(--font-size-xs)", color: "var(--accent-gold)", fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, marginBottom: "var(--space-sm)" }}>
                🌱 {t("prevention")}
              </p>
              <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "var(--space-xs)" }}>
                {result.prevention_tips.map((tip, idx) => (
                  <li
                    key={idx}
                    style={{
                      fontSize: "var(--font-size-sm)",
                      color: "var(--text-tertiary)",
                      display: "flex",
                      gap: "var(--space-sm)",
                    }}
                  >
                    <span style={{ color: "var(--accent-gold)" }}>•</span>
                    {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Precautions Card */}
        <div className="card card-shimmer" style={{ borderColor: "var(--accent-orange)" }}>
          <div className="badge badge-orange" style={{ marginBottom: "var(--space-lg)" }}>
            ⚠️ {t("precautions")}
          </div>

          <ul className="precaution-list">
            {result.precautions?.map((precaution, idx) => (
              <li className="precaution-item" key={idx}>
                {precaution}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Feedback Section */}
      <RevealSection className="feedback-section" delay={200}>
        {feedbackGiven ? (
          <div>
            <div style={{ fontSize: 48, marginBottom: "var(--space-md)" }}>
              {feedbackType === "correct" ? "✅" : "📝"}
            </div>
            <h3 className="feedback-title">
              {feedbackType === "correct"
                ? "Thank you! Your feedback helps improve the model."
                : "Thank you! We'll use your correction to improve accuracy."}
            </h3>
            <p style={{ color: "var(--text-tertiary)", fontSize: "var(--font-size-sm)" }}>
              Verified data feeds back into the district&apos;s training set → Model continuously improves
            </p>
          </div>
        ) : (
          <>
            <div style={{ fontSize: 32, marginBottom: "var(--space-sm)" }}>🔄</div>
            <h3 className="feedback-title">
              {t("feedback_title")}
            </h3>
            <p className="feedback-subtitle">
              {t("feedback_desc") || "Your feedback helps improve the AI model for your district."}
            </p>
            <div className="feedback-actions">
              <button
                className="btn btn-primary"
                onClick={() => handleFeedback(true)}
                id="feedback-yes"
              >
                ✓ {t("feedback_yes")}
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => handleFeedback(false)}
                id="feedback-no"
              >
                ✗ {t("feedback_no")}
              </button>
            </div>
          </>
        )}
      </RevealSection>

      {/* Actions */}
      <div style={{ display: "flex", gap: "var(--space-md)", justifyContent: "center", marginTop: "var(--space-2xl)" }}>
        <a href="/diagnose" className="btn btn-primary">
          📸 New Diagnosis
        </a>
        <a href="/history" className="btn btn-secondary">
          📋 View History
        </a>
      </div>
    </div>
  );
}

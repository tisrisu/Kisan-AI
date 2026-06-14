"use client";

/**
 * KisanAI — Diagnose Page
 * Upload leaf photo + metadata → Submit for AI diagnosis.
 * Uses i18n and responsive diagnose-grid class.
 */

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import api, { DEMO_DISTRICTS, DEMO_CROPS, DEMO_RESULT } from "@/lib/api";
import { useLanguage } from "@/lib/LanguageProvider";

export default function DiagnosePage() {
  const router = useRouter();
  const fileInputRef = useRef(null);
  const { t } = useLanguage();

  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [cropVarietyId, setCropVarietyId] = useState("");
  const [districtId, setDistrictId] = useState("");
  const [season, setSeason] = useState("kharif");
  const [symptomText, setSymptomText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  // Handle image selection
  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        alert("Image too large. Maximum size is 10MB.");
        return;
      }
      setImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  // Handle drag & drop
  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file && (file.type === "image/jpeg" || file.type === "image/png")) {
      setImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  // Voice input using Web Speech API
  const handleVoiceInput = () => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      alert("Voice input is not supported in this browser. Please use Chrome.");
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "hi-IN"; // Hindi by default, multilingual

    recognition.onstart = () => setIsRecording(true);
    recognition.onend = () => setIsRecording(false);
    recognition.onerror = () => setIsRecording(false);

    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      setSymptomText((prev) => prev + " " + transcript);
    };

    if (isRecording) {
      recognition.stop();
    } else {
      recognition.start();
    }
  };

  // Submit diagnosis
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!image) {
      alert("Please upload a leaf photo first.");
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("image", image);
      formData.append("crop_variety_id", cropVarietyId || "0");
      formData.append("district_id", districtId || "0");
      formData.append("season", season);
      formData.append("symptom_text", symptomText);

      const result = await api.diagnose(formData);

      if (result) {
        // Store result and navigate to results page
        sessionStorage.setItem("diagnosis_result", JSON.stringify(result));
        sessionStorage.setItem("uploaded_image", imagePreview);
        router.push(`/results/${result.diagnosis_id || "demo"}`);
      } else {
        // Use demo data when API is offline
        sessionStorage.setItem("diagnosis_result", JSON.stringify(DEMO_RESULT));
        sessionStorage.setItem("uploaded_image", imagePreview);
        router.push("/results/demo");
      }
    } catch (error) {
      console.error("Diagnosis failed:", error);
      // Fallback to demo
      sessionStorage.setItem("diagnosis_result", JSON.stringify(DEMO_RESULT));
      sessionStorage.setItem("uploaded_image", imagePreview);
      router.push("/results/demo");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container" style={{ padding: "var(--space-3xl) var(--space-xl)" }}>
      {/* Header */}
      <div className="animate-in" style={{ marginBottom: "var(--space-2xl)" }}>
        <div className="section-label">🔬 {t("diag_label")}</div>
        <h1 className="section-title">{t("diag_title")}</h1>
        <p className="section-subtitle">
          {t("diag_subtitle")}
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="diagnose-grid">
          {/* Left Column — Image Upload */}
          <div className="animate-in animate-delay-1">
            <div
              className={`upload-area ${dragOver ? "drag-over" : ""}`}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              id="upload-area"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png"
                onChange={handleImageChange}
                style={{ display: "none" }}
                id="image-upload"
              />

              {imagePreview ? (
                <div>
                  <img
                    src={imagePreview}
                    alt="Uploaded leaf"
                    className="upload-preview"
                  />
                  <p style={{ marginTop: "var(--space-md)", color: "var(--accent-green)", fontSize: "var(--font-size-sm)", fontWeight: 600 }}>
                    ✓ Image uploaded — click to change
                  </p>
                </div>
              ) : (
                <>
                  <div className="upload-icon">📸</div>
                  <h3 className="upload-title">{t("upload_photo")}</h3>
                  <p className="upload-subtitle">
                    {t("upload_drag")}
                    <br />
                    <span style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)" }}>
                      {t("upload_formats")}
                    </span>
                  </p>
                </>
              )}
            </div>
          </div>

          {/* Right Column — Metadata Form */}
          <div className="animate-in animate-delay-2">
            {/* Crop Variety */}
            <div className="form-group">
              <label className="form-label" htmlFor="crop-variety">{t("crop_variety")}</label>
              <select
                id="crop-variety"
                className="form-select"
                value={cropVarietyId}
                onChange={(e) => setCropVarietyId(e.target.value)}
              >
                <option value="">{t("crop_placeholder")}</option>
                {Object.entries(
                  DEMO_CROPS.reduce((acc, crop) => {
                    if (!acc[crop.category]) acc[crop.category] = [];
                    acc[crop.category].push(crop);
                    return acc;
                  }, {})
                ).map(([category, crops]) => (
                  <optgroup key={category} label={category}>
                    {crops.map((crop) => (
                      <option key={crop.id} value={crop.id}>
                        {crop.name}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>

            {/* District */}
            <div className="form-group">
              <label className="form-label" htmlFor="district">{t("district")}</label>
              <select
                id="district"
                className="form-select"
                value={districtId}
                onChange={(e) => setDistrictId(e.target.value)}
              >
                <option value="">{t("district_placeholder")}</option>
                {Object.entries(
                  DEMO_DISTRICTS.reduce((acc, d) => {
                    if (!acc[d.state]) acc[d.state] = [];
                    acc[d.state].push(d);
                    return acc;
                  }, {})
                ).map(([state, districts]) => (
                  <optgroup key={state} label={state}>
                    {districts.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>

            {/* Season */}
            <div className="form-group">
              <label className="form-label">{t("season")}</label>
              <div className="radio-group">
                {[
                  { value: "kharif", key: "season_kharif" },
                  { value: "rabi", key: "season_rabi" },
                  { value: "zaid", key: "season_zaid" },
                ].map((s) => (
                  <div className="radio-option" key={s.value}>
                    <input
                      type="radio"
                      id={`season-${s.value}`}
                      name="season"
                      value={s.value}
                      checked={season === s.value}
                      onChange={(e) => setSeason(e.target.value)}
                    />
                    <label htmlFor={`season-${s.value}`}>{t(s.key)}</label>
                  </div>
                ))}
              </div>
            </div>

            {/* Symptom Text */}
            <div className="form-group">
              <label className="form-label" htmlFor="symptoms">
                {t("symptoms")}
                <span style={{ color: "var(--text-muted)", fontWeight: 400, marginLeft: 8 }}>
                  (any language)
                </span>
              </label>
              <div style={{ display: "flex", gap: "var(--space-sm)", alignItems: "flex-start" }}>
                <textarea
                  id="symptoms"
                  className="form-textarea"
                  placeholder={t("symptoms_placeholder")}
                  value={symptomText}
                  onChange={(e) => setSymptomText(e.target.value)}
                  style={{ flex: 1 }}
                />
                <button
                  type="button"
                  className={`voice-btn ${isRecording ? "recording" : ""}`}
                  onClick={handleVoiceInput}
                  title={t("voice_input")}
                  id="voice-input-btn"
                >
                  🎤
                </button>
              </div>
              {isRecording && (
                <p style={{ color: "var(--accent-coral)", fontSize: "var(--font-size-xs)", marginTop: 4, animation: "pulse 1s ease-in-out infinite" }}>
                  🔴 Recording... speak your symptoms
                </p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="btn btn-primary btn-lg glow-pulse"
              style={{ width: "100%" }}
              disabled={isLoading || !image}
              id="submit-diagnosis"
            >
              {isLoading ? (
                <>
                  <span className="spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
                  {t("analyzing")}
                </>
              ) : (
                `🔬 ${t("submit_diagnosis")}`
              )}
            </button>

            {!image && (
              <p style={{ color: "var(--text-muted)", fontSize: "var(--font-size-xs)", textAlign: "center", marginTop: "var(--space-sm)" }}>
                Please upload a leaf photo to continue
              </p>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}

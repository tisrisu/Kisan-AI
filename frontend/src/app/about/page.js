"use client";

/**
 * KisanAI — About Page
 * Mission, technology, and team information.
 */

import { useLanguage } from "@/lib/LanguageProvider";
import { RevealSection } from "@/lib/animations";

export default function AboutPage() {
  const { t } = useLanguage();

  const timeline = [
    { icon: "📸", title: "Farmer Uploads", desc: "A farmer photographs a diseased leaf using their smartphone — even a basic Android device works." },
    { icon: "🧠", title: "Multi-Modal AI", desc: "Our AI analyzes the image alongside text symptoms, district context, and seasonal data for maximum accuracy." },
    { icon: "💊", title: "Instant Diagnosis", desc: "Within seconds, the farmer receives disease identification, severity grading, and recommended medications." },
    { icon: "🔄", title: "Continuous Learning", desc: "Expert-verified diagnoses feed back into the model. The AI gets smarter for each district over time." },
  ];

  const techStack = [
    { name: "EfficientNet-B4", category: "Vision Model", desc: "Pretrained on ImageNet, fine-tuned for leaf disease recognition. Handles 380×380 input images." },
    { name: "Multilingual BERT", category: "Text Encoder", desc: "Processes symptom descriptions in Hindi, Tamil, Telugu, and English for multi-lingual understanding." },
    { name: "Multi-Modal Fusion", category: "Architecture", desc: "Concatenates image (1792-d), text (256-d), and context (64-d) embeddings for joint classification." },
    { name: "Per-District Fine-Tuning", category: "Adaptation", desc: "Once 50+ verified samples exist for a district, the model automatically adapts to local conditions." },
    { name: "FastAPI + PostgreSQL", category: "Backend", desc: "High-performance Python API with vector store for embeddings and MinIO for image storage." },
    { name: "Next.js PWA", category: "Frontend", desc: "Installable progressive web app with offline support and 4-language interface." },
  ];

  const values = [
    { icon: "🌾", title: "Farmer-First Design", desc: "Every decision prioritizes the smallholder farmer — offline support, vernacular languages, sub-second responses on budget phones." },
    { icon: "🔬", title: "Scientific Rigor", desc: "Our training pipeline uses peer-reviewed datasets (PlantVillage, PlantDoc) and expert-validated regional data from ICAR." },
    { icon: "🛡️", title: "Honest AI", desc: "When our model is unsure, it says so. We never provide a false-confident diagnosis — uncertain cases route to human experts." },
    { icon: "🌍", title: "Open Knowledge", desc: "We believe crop disease intelligence should be accessible to every farmer. Our approach democratizes agricultural AI." },
  ];

  return (
    <div style={{ paddingBottom: "var(--space-3xl)" }}>
      {/* Hero Section */}
      <section className="page-section" style={{ background: "var(--bg-secondary)", textAlign: "center" }}>
        <div className="container">
          <div className="animate-in">
            <div className="section-label">🌿 ABOUT KISANAI</div>
            <h1 className="section-title" style={{ maxWidth: 700, margin: "0 auto var(--space-md)" }}>
              Building an AI That{" "}
              <span className="gradient-text-animated">Learns From India&apos;s Fields</span>
            </h1>
            <p className="section-subtitle" style={{ maxWidth: 600, margin: "0 auto" }}>
              KisanAI is a multi-modal crop disease diagnosis platform that combines computer vision,
              natural language processing, and regional context to deliver accurate, actionable intelligence
              to Indian farmers — in their own language.
            </p>
          </div>
        </div>
      </section>

      {/* Mission */}
      <section className="page-section">
        <div className="container">
          <RevealSection>
            <div className="card card-glass glow-pulse" style={{ borderColor: "var(--accent-green)", padding: "var(--space-2xl)", maxWidth: 850, margin: "0 auto", textAlign: "center" }}>
              <div className="badge badge-green" style={{ marginBottom: "var(--space-md)" }}>🎯 OUR MISSION</div>
              <h2 style={{ fontSize: "var(--font-size-2xl)", fontWeight: 800, marginBottom: "var(--space-md)" }}>
                Every Misdiagnosis Avoided Is a Family Fed
              </h2>
              <p style={{ color: "var(--text-tertiary)", lineHeight: 1.8, fontSize: "var(--font-size-base)" }}>
                India loses <strong style={{ color: "var(--accent-coral)" }}>~₹50,000 Crore annually</strong> to crop diseases.
                70% of our farmers lack access to expert diagnosis. A single wrong pesticide application wastes money,
                poisons soil, and still loses the crop. We&apos;re building AI that changes this — district by district.
              </p>
            </div>
          </RevealSection>
        </div>
      </section>

      {/* How It Works Timeline */}
      <section className="page-section" style={{ background: "var(--bg-secondary)" }}>
        <div className="container">
          <RevealSection>
            <div className="section-label" style={{ textAlign: "center" }}>🔄 HOW IT WORKS</div>
            <h2 className="section-title" style={{ textAlign: "center" }}>From Field to Diagnosis in Seconds</h2>
          </RevealSection>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "var(--space-lg)", marginTop: "var(--space-2xl)" }}>
            {timeline.map((step, idx) => (
              <RevealSection key={idx} delay={idx * 150}>
                <div className="card card-shimmer" style={{ textAlign: "center", padding: "var(--space-2xl) var(--space-lg)", height: "100%" }}>
                  <div style={{ fontSize: 40, marginBottom: "var(--space-md)" }}>{step.icon}</div>
                  <div className="badge badge-green" style={{ marginBottom: "var(--space-sm)" }}>Step {idx + 1}</div>
                  <h3 style={{ fontSize: "var(--font-size-lg)", fontWeight: 700, marginBottom: "var(--space-sm)" }}>{step.title}</h3>
                  <p style={{ color: "var(--text-tertiary)", fontSize: "var(--font-size-sm)", lineHeight: 1.7 }}>{step.desc}</p>
                </div>
              </RevealSection>
            ))}
          </div>
        </div>
      </section>

      {/* Our Values */}
      <section className="page-section">
        <div className="container">
          <RevealSection>
            <div className="section-label">💎 OUR VALUES</div>
            <h2 className="section-title">What Drives Us</h2>
          </RevealSection>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "var(--space-lg)", marginTop: "var(--space-2xl)" }}>
            {values.map((val, idx) => (
              <RevealSection key={idx} delay={idx * 100}>
                <div className="card card-shimmer" style={{ height: "100%" }}>
                  <div style={{ fontSize: 32, marginBottom: "var(--space-md)" }}>{val.icon}</div>
                  <h3 style={{ fontSize: "var(--font-size-lg)", fontWeight: 700, marginBottom: "var(--space-sm)" }}>{val.title}</h3>
                  <p style={{ color: "var(--text-tertiary)", fontSize: "var(--font-size-sm)", lineHeight: 1.7 }}>{val.desc}</p>
                </div>
              </RevealSection>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="page-section" style={{ background: "var(--bg-secondary)" }}>
        <div className="container">
          <RevealSection>
            <div className="section-label">🛠️ TECHNOLOGY</div>
            <h2 className="section-title">Under the Hood</h2>
            <p className="section-subtitle" style={{ marginBottom: "var(--space-2xl)" }}>
              Built with state-of-the-art ML, modern web technologies, and designed for scale
            </p>
          </RevealSection>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "var(--space-lg)" }}>
            {techStack.map((tech, idx) => (
              <RevealSection key={idx} delay={idx * 100}>
                <div className="card card-shimmer" style={{ height: "100%" }}>
                  <div className="badge badge-green" style={{ marginBottom: "var(--space-md)" }}>{tech.category}</div>
                  <h3 style={{ fontSize: "var(--font-size-lg)", fontWeight: 700, marginBottom: "var(--space-sm)", color: "var(--accent-green)" }}>{tech.name}</h3>
                  <p style={{ color: "var(--text-tertiary)", fontSize: "var(--font-size-sm)", lineHeight: 1.7 }}>{tech.desc}</p>
                </div>
              </RevealSection>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="page-section" style={{ textAlign: "center" }}>
        <div className="container">
          <RevealSection>
            <div style={{ fontSize: 48, marginBottom: "var(--space-md)" }}>🌱</div>
            <h2 className="section-title">Join the Movement</h2>
            <p className="section-subtitle" style={{ margin: "0 auto var(--space-2xl)", maxWidth: 550 }}>
              Every diagnosis verified, every photo uploaded, makes KisanAI smarter for farmers across India.
            </p>
            <div style={{ display: "flex", gap: "var(--space-md)", justifyContent: "center", flexWrap: "wrap" }}>
              <a href="/diagnose" className="btn btn-primary btn-lg glow-pulse">
                🔬 Try It Now
              </a>
              <a href="/dashboard" className="btn btn-secondary btn-lg">
                📊 View Dashboard
              </a>
            </div>
          </RevealSection>
        </div>
      </section>
    </div>
  );
}

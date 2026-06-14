/**
 * KisanAI — Footer Component
 * Server-friendly footer with navigation links.
 */

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-grid">
        <div className="footer-brand">
          <a href="/" className="navbar-brand" style={{ marginBottom: "8px" }}>
            <span className="brand-icon">🌿</span>
            <span className="brand-text">KisanAI</span>
          </a>
          <p>
            AI-powered crop disease diagnosis for Indian farmers. Multi-modal
            fusion with per-district fine-tuning.
          </p>
        </div>

        <div>
          <h4 className="footer-heading">Platform</h4>
          <ul className="footer-links">
            <li><a href="/diagnose">Diagnose</a></li>
            <li><a href="/history">History</a></li>
            <li><a href="/dashboard">Dashboard</a></li>
            <li><a href="/about">About</a></li>
          </ul>
        </div>

      </div>

      <div className="footer-bottom">
        <p>© 2024 KisanAI. Built for India&apos;s farmers. All open-source • Python-first • GPU-optimized</p>
      </div>
    </footer>
  );
}

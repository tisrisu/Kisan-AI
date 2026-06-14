"use client";

/**
 * KisanAI — Navbar Component
 * Client component with mobile hamburger menu, active link highlighting,
 * and functional language switcher wired to i18n context.
 */

import { useState, useEffect } from "react";
import { useLanguage } from "@/lib/LanguageProvider";

const NAV_LINKS = [
  { href: "/", key: "nav_home", fallback: "Home" },
  { href: "/diagnose", key: "nav_diagnose", fallback: "Diagnose" },
  { href: "/history", key: "nav_history", fallback: "History" },
  { href: "/dashboard", key: "nav_dashboard", fallback: "Dashboard" },
  { href: "/about", key: "nav_about", fallback: "About" },
];

const LANG_OPTIONS = [
  { code: "en", label: "EN" },
  { code: "hi", label: "हि" },
  { code: "te", label: "తె" },
  { code: "ta", label: "த" },
];

export default function Navbar() {
  const { lang, setLang, t } = useLanguage();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [currentPath, setCurrentPath] = useState("/");

  useEffect(() => {
    setCurrentPath(window.location.pathname);

    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [currentPath]);

  // Prevent body scroll when mobile menu open
  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  const isActive = (href) => {
    if (href === "/") return currentPath === "/";
    return currentPath.startsWith(href);
  };

  return (
    <>
      <nav className={`navbar ${scrolled ? "navbar-scrolled" : ""}`} id="navbar">
        <div className="navbar-inner">
          <a href="/" className="navbar-brand">
            <span className="brand-icon">🌿</span>
            <span className="brand-text">KisanAI</span>
          </a>

          {/* Desktop Navigation */}
          <ul className="navbar-nav">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  className={isActive(link.href) ? "active" : ""}
                >
                  {t(link.key) || link.fallback}
                </a>
              </li>
            ))}
          </ul>

          <div className="navbar-actions">
            {/* Language Switcher */}
            <div className="lang-switcher" id="lang-switcher">
              {LANG_OPTIONS.map((opt) => (
                <button
                  key={opt.code}
                  className={`lang-btn ${lang === opt.code ? "active" : ""}`}
                  data-lang={opt.code}
                  onClick={() => setLang(opt.code)}
                  type="button"
                  aria-label={`Switch to ${opt.code}`}
                >
                  {opt.label}
                </button>
              ))}
            </div>

            {/* CTA Button (desktop) */}
            <a href="/diagnose" className="btn btn-primary btn-sm navbar-cta">
              {t("hero_cta") || "Start Diagnosis"}
            </a>

            {/* Hamburger Button (mobile) */}
            <button
              className={`hamburger ${mobileOpen ? "open" : ""}`}
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-label="Toggle navigation menu"
              aria-expanded={mobileOpen}
              type="button"
              id="hamburger-btn"
            >
              <span className="hamburger-line" />
              <span className="hamburger-line" />
              <span className="hamburger-line" />
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      <div
        className={`mobile-overlay ${mobileOpen ? "open" : ""}`}
        onClick={() => setMobileOpen(false)}
        aria-hidden="true"
      />

      {/* Mobile Menu Drawer */}
      <div className={`mobile-drawer ${mobileOpen ? "open" : ""}`} id="mobile-menu">
        <div className="mobile-drawer-header">
          <a href="/" className="navbar-brand" onClick={() => setMobileOpen(false)}>
            <span className="brand-icon">🌿</span>
            <span className="brand-text">KisanAI</span>
          </a>
        </div>

        <ul className="mobile-nav">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className={isActive(link.href) ? "active" : ""}
                onClick={() => setMobileOpen(false)}
              >
                {t(link.key) || link.fallback}
              </a>
            </li>
          ))}
        </ul>

        {/* Mobile Language Switcher */}
        <div className="mobile-lang-section">
          <p className="mobile-lang-label">Language</p>
          <div className="lang-switcher mobile-lang-switcher">
            {LANG_OPTIONS.map((opt) => (
              <button
                key={opt.code}
                className={`lang-btn ${lang === opt.code ? "active" : ""}`}
                onClick={() => setLang(opt.code)}
                type="button"
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <a
          href="/diagnose"
          className="btn btn-primary btn-lg"
          style={{ width: "100%", marginTop: "auto" }}
          onClick={() => setMobileOpen(false)}
        >
          🔬 {t("hero_cta") || "Start Diagnosis"}
        </a>
      </div>
    </>
  );
}

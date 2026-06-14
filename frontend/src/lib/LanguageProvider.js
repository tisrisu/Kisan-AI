"use client";

/**
 * KisanAI — Language Context Provider
 * Provides i18n support across the entire app.
 * Persists language choice to localStorage.
 */

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import translations from "./i18n";

const LanguageContext = createContext({
  lang: "en",
  setLang: () => {},
  t: (key) => key,
});

export function LanguageProvider({ children }) {
  const [lang, setLangState] = useState("en");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Read persisted language on mount
    const saved = localStorage.getItem("kisanai_lang");
    if (saved && translations[saved]) {
      setLangState(saved);
    }
    setMounted(true);
  }, []);

  const setLang = useCallback((newLang) => {
    if (translations[newLang]) {
      setLangState(newLang);
      localStorage.setItem("kisanai_lang", newLang);
      document.documentElement.lang = newLang;
    }
  }, []);

  const t = useCallback(
    (key) => {
      return translations[lang]?.[key] || translations.en?.[key] || key;
    },
    [lang]
  );

  // Prevent hydration mismatch by rendering children only after mount
  // but still render the structure to avoid layout shift
  const value = { lang: mounted ? lang : "en", setLang, t };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}

export default LanguageContext;

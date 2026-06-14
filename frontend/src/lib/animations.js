"use client";

/**
 * KisanAI — Scroll Reveal Hook
 * Uses IntersectionObserver to trigger reveal animations when elements scroll into view.
 */

import { useEffect, useRef } from "react";

export function useScrollReveal(options = {}) {
  const ref = useRef(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          element.classList.add("revealed");
          observer.unobserve(element);
        }
      },
      {
        threshold: options.threshold || 0.15,
        rootMargin: options.rootMargin || "0px 0px -40px 0px",
      }
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [options.threshold, options.rootMargin]);

  return ref;
}

/**
 * Animated counter hook — counts up from 0 to target value
 */
export function useAnimatedCounter(target, duration = 2000, startOnReveal = true) {
  const ref = useRef(null);
  const countRef = useRef(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const animate = () => {
      const start = performance.now();
      const numericTarget = parseFloat(String(target).replace(/[^0-9.]/g, ""));
      const suffix = String(target).replace(/[0-9.]/g, "");
      const isFloat = String(target).includes(".");

      const step = (now) => {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = eased * numericTarget;

        if (countRef.current) {
          countRef.current.textContent = (isFloat ? current.toFixed(1) : Math.round(current)) + suffix;
        }

        if (progress < 1) {
          requestAnimationFrame(step);
        }
      };

      requestAnimationFrame(step);
    };

    if (startOnReveal) {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            animate();
            observer.unobserve(element);
          }
        },
        { threshold: 0.3 }
      );
      observer.observe(element);
      return () => observer.disconnect();
    } else {
      animate();
    }
  }, [target, duration, startOnReveal]);

  return { containerRef: ref, countRef };
}

/**
 * Component wrapper for scroll-reveal sections
 */
export function RevealSection({ children, className = "", delay = 0, ...props }) {
  const ref = useScrollReveal();

  return (
    <div
      ref={ref}
      className={`reveal-on-scroll ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
      {...props}
    >
      {children}
    </div>
  );
}

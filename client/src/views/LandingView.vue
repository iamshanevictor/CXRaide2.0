<template>
  <div class="landing">
    <div class="bg" aria-hidden="true">
      <div class="bg-grid" />
      <div class="float f1" />
      <div class="float f2" />
      <div class="float f3" />
      <div class="glow g1" />
      <div class="glow g2" />
    </div>

    <header class="nav">
      <div class="container nav-inner">
        <RouterLink class="brand" to="/">
          <img class="brand-logo" src="@/assets/LOGO2.png" alt="CXRaide" />
        </RouterLink>

        <nav class="nav-links" aria-label="Primary">
          <a href="#features">Features</a>
          <a href="#workflow">How it works</a>
          <a href="#security">Security</a>
          <a href="#contact">Contact</a>
        </nav>

        <div class="nav-cta">
          <RouterLink class="nav-link" to="/login">Sign in</RouterLink>
          <a class="btn btn-ghost" href="#contact">Request demo</a>
          <RouterLink class="btn btn-primary" to="/login">Try the app</RouterLink>
        </div>
      </div>
    </header>

    <main>
      <section class="hero" aria-labelledby="hero-title">
        <div class="container hero-inner">
          <div class="hero-copy">
            <div class="badge">
              <span class="badge-dot" />
              <span>Designed for fast, consistent CXR workflows</span>
            </div>

            <h1 id="hero-title">Secure annotation for fast‑moving research teams</h1>
            <p class="lead">
              CXRaide 2.0 helps you upload CXRs, review AI outputs, and capture structured annotations—without turning
              labeling into a fragile spreadsheet project.
            </p>

            <div class="actions">
              <RouterLink class="btn btn-primary" to="/login">Try CXRaide</RouterLink>
              <a class="btn btn-ghost" href="#workflow">How it works</a>
            </div>

            <div class="logo-strip" aria-label="Designed for">
              <span class="logo-pill">Radiology labs</span>
              <span class="logo-pill">Academic cohorts</span>
              <span class="logo-pill">Clinical research</span>
              <span class="logo-pill">AI teams</span>
              <span class="logo-pill">Hospitals</span>
            </div>
          </div>

          <div class="hero-preview" aria-label="Product preview">
            <div class="preview-card">
              <div class="preview-head">
                <div class="preview-title">Review session</div>
                <div class="preview-status">
                  <span class="status-dot" />
                  <span>Verified</span>
                </div>
              </div>

              <div class="preview-body">
                <div class="preview-row">
                  <span class="k">Study</span>
                  <span class="v">CXR_0421</span>
                </div>
                <div class="preview-row">
                  <span class="k">Reviewer</span>
                  <span class="v">Assigned · 2 of 3</span>
                </div>
                <div class="preview-row">
                  <span class="k">Model</span>
                  <span class="v">IT3 · containerized</span>
                </div>

                <div class="preview-metrics" aria-label="Quality signals">
                  <div class="metric">
                    <div class="metric-name">Coverage</div>
                    <div class="metric-bar"><span style="width: 82%" /></div>
                    <div class="metric-val">82%</div>
                  </div>
                  <div class="metric">
                    <div class="metric-name">Consensus</div>
                    <div class="metric-bar"><span style="width: 67%" /></div>
                    <div class="metric-val">67%</div>
                  </div>
                </div>

                <div class="preview-note">
                  Tokens verify server‑side; local dev runs without a database.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="workflow" class="section" aria-labelledby="how-title">
        <div class="container">
          <h2 id="how-title" class="section-title">How CXRaide works</h2>
          <p class="section-sub">
            A simple loop: authenticate, upload, and annotate—with safeguards for reliability.
          </p>

          <div class="cards">
            <article class="card">
              <div class="card-icon">▣</div>
              <h3>Map studies</h3>
              <p>Organize images into repeatable tasks so reviewers always see the right context.</p>
            </article>
            <article class="card">
              <div class="card-icon">◎</div>
              <h3>Assign reviewers</h3>
              <p>Use Firebase auth (or local dev auth) to control access and keep sessions consistent.</p>
            </article>
            <article class="card">
              <div class="card-icon">⟡</div>
              <h3>Annotate anywhere</h3>
              <p>Run locally with Docker, or deploy later—same interface, same workflow.</p>
            </article>
          </div>
        </div>
      </section>

      <section id="features" class="section section-alt" aria-labelledby="features-title">
        <div class="container">
          <h2 id="features-title" class="section-title">Features</h2>
          <p class="section-sub">Built for speed, safety, and clean evaluation data.</p>

          <div class="feature-grid">
            <div class="feature">
              <div class="feature-title">Upload → inference</div>
              <div class="feature-text">Predictable API workflow with responsive UI.</div>
            </div>
            <div class="feature">
              <div class="feature-title">Structured annotations</div>
              <div class="feature-text">Guardrails and defaults reduce label noise.</div>
            </div>
            <div class="feature">
              <div class="feature-title">Developer-friendly</div>
              <div class="feature-text">Vite + Flask + Docker for stable local iteration.</div>
            </div>
            <div class="feature">
              <div class="feature-title">Model-aware</div>
              <div class="feature-text">Supports IT2 / IT3 weights in Docker.</div>
            </div>
          </div>
        </div>
      </section>

      <section id="security" class="section" aria-labelledby="security-title">
        <div class="container">
          <h2 id="security-title" class="section-title">Security posture</h2>
          <p class="section-sub">Auth tokens verified server-side; local secrets are kept out of git.</p>

          <div class="feature-grid">
            <div class="feature">
              <div class="feature-title">No secrets committed</div>
              <div class="feature-text">Env files and service-account JSON are git-ignored by default.</div>
            </div>
            <div class="feature">
              <div class="feature-title">Token verification</div>
              <div class="feature-text">Firebase ID tokens (Admin SDK) or local JWT for development.</div>
            </div>
            <div class="feature">
              <div class="feature-title">Clear separation</div>
              <div class="feature-text">Frontend auth stays modular; backend stays stateless.</div>
            </div>
            <div class="feature">
              <div class="feature-title">CORS-aware</div>
              <div class="feature-text">Configured for local + hosted environments.</div>
            </div>
          </div>
        </div>
      </section>

      <section id="contact" class="section section-alt" aria-labelledby="contact-title">
        <div class="container footer">
          <div class="footer-left">
            <div class="footer-brand">CXRaide 2.0</div>
            <div class="footer-muted">Assistive CXR annotation and classification UI.</div>
          </div>
          <div class="footer-right">
            <RouterLink class="nav-link" to="/login">Sign in</RouterLink>
            <a class="nav-link" href="#features">Features</a>
            <a class="nav-link" href="#workflow">How it works</a>
            <a class="nav-link" href="#security">Security</a>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
export default {
  name: "LandingView",
};
</script>

<style scoped>
.landing {
  min-height: 100vh;
  color: #e2e8f0;
  background: linear-gradient(135deg, #090c14 0%, #10172a 100%);
  position: relative;
  overflow-x: hidden;
}

.container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 20px;
}

.bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 1px 1px, rgba(148, 163, 184, 0.10) 1px, transparent 0);
  background-size: 42px 42px;
  mask-image: radial-gradient(600px 400px at 50% 18%, rgba(0, 0, 0, 1) 40%, rgba(0, 0, 0, 0) 100%);
  opacity: 0.9;
}

.glow {
  position: absolute;
  width: 680px;
  height: 680px;
  border-radius: 999px;
  filter: blur(60px);
  opacity: 0.25;
}

.g1 {
  left: -220px;
  top: -260px;
  background: radial-gradient(circle at 30% 30%, rgba(59, 130, 246, 1), transparent 60%);
}

.g2 {
  right: -260px;
  top: -200px;
  background: radial-gradient(circle at 30% 30%, rgba(96, 165, 250, 1), transparent 60%);
}

.float {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 3px;
  background: rgba(59, 130, 246, 0.16);
  border: 1px solid rgba(59, 130, 246, 0.18);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

.f1 {
  left: 10%;
  top: 22%;
  transform: rotate(10deg);
}

.f2 {
  right: 14%;
  top: 18%;
  transform: rotate(-12deg);
  background: rgba(99, 102, 241, 0.16);
  border-color: rgba(99, 102, 241, 0.18);
}

.f3 {
  left: 22%;
  top: 55%;
  transform: rotate(8deg);
  background: rgba(148, 163, 184, 0.10);
  border-color: rgba(148, 163, 184, 0.14);
}

.nav {
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(10px);
  background: rgba(15, 23, 42, 0.68);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.nav-inner {
  padding: 14px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.brand-logo {
  height: 28px;
  width: auto;
  display: block;
}

.brand-text {
  display: inline-flex;
  align-items: baseline;
  gap: 0;
  font-size: 18px;
  line-height: 1;
}

.brand-logo {
  height: 30px;
  width: auto;
  display: block;
}

.brand-title {
  font-weight: 950;
  letter-spacing: -0.04em;
  color: #60a5fa;
}

.brand-version {
  font-size: 12px;
  opacity: 0.75;
  margin-left: 6px;
  color: rgba(226, 232, 240, 0.9);
}

.nav-links {
  display: none;
  gap: 18px;
}

.nav-links a,
.nav-link {
  color: rgba(226, 232, 240, 0.72);
  text-decoration: none;
  font-weight: 700;
  font-size: 13px;
}

.nav-links a:hover,
.nav-link:hover {
  color: rgba(226, 232, 240, 0.96);
}

.nav-cta {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 14px;
  border-radius: 12px;
  font-weight: 800;
  font-size: 13px;
  text-decoration: none;
  border: 1px solid transparent;
  cursor: pointer;
  user-select: none;
  transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.12s ease;
  white-space: nowrap;
}

.btn:active {
  transform: translateY(1px);
}

.btn-primary {
  color: #ffffff;
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  box-shadow: 0 10px 24px rgba(59, 130, 246, 0.22);
}

.btn-primary:hover {
  box-shadow: 0 14px 28px rgba(59, 130, 246, 0.28);
}

.btn-secondary {
  color: rgba(226, 232, 240, 0.9);
  background: rgba(15, 23, 42, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}

.btn-secondary:hover {
  background: rgba(15, 23, 42, 0.7);
}

.btn-ghost {
  color: rgba(226, 232, 240, 0.9);
  background: rgba(15, 23, 42, 0.35);
  border-color: rgba(255, 255, 255, 0.14);
}

.btn-ghost:hover {
  background: rgba(15, 23, 42, 0.55);
}

.hero {
  padding: 84px 0 38px;
}

.hero-inner {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 28px;
  align-items: center;
}

.hero-copy {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.10);
  font-weight: 800;
  font-size: 12px;
  color: rgba(226, 232, 240, 0.78);
}

.badge-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.14);
}

.hero-copy h1 {
  margin-top: 18px;
  font-size: 46px;
  line-height: 1.06;
  letter-spacing: -0.04em;
  max-width: 20ch;
}

.lead {
  margin-top: 14px;
  font-size: 15px;
  line-height: 1.7;
  color: rgba(148, 163, 184, 0.95);
  max-width: 62ch;
}

.actions {
  margin-top: 18px;
  display: inline-flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.logo-strip {
  margin-top: 28px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  opacity: 0.9;
}

.hero-preview {
  display: flex;
  justify-content: center;
}

.preview-card {
  width: 100%;
  max-width: 520px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.10);
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.36);
  overflow: hidden;
}

.preview-head {
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.preview-title {
  font-weight: 950;
  letter-spacing: -0.02em;
}

.preview-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 850;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.95);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.14);
}

.preview-body {
  padding: 14px 16px 16px;
}

.preview-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.12);
}

.preview-row:last-of-type {
  border-bottom: none;
}

.k {
  font-weight: 900;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.95);
}

.v {
  font-weight: 900;
  font-size: 12px;
  color: rgba(226, 232, 240, 0.95);
}

.preview-metrics {
  margin-top: 14px;
  display: grid;
  gap: 10px;
}

.metric {
  display: grid;
  grid-template-columns: 90px 1fr 44px;
  gap: 10px;
  align-items: center;
}

.metric-name {
  font-weight: 900;
  font-size: 11px;
  color: rgba(148, 163, 184, 0.95);
}

.metric-bar {
  height: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  overflow: hidden;
}

.metric-bar span {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.metric-val {
  text-align: right;
  font-weight: 900;
  font-size: 11px;
  color: rgba(148, 163, 184, 0.95);
}

.preview-note {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(148, 163, 184, 0.95);
  font-weight: 750;
  font-size: 12px;
  line-height: 1.5;
}

.logo-pill {
  padding: 10px 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.40);
  border: 1px solid rgba(255, 255, 255, 0.10);
  color: rgba(148, 163, 184, 0.95);
  font-weight: 900;
  font-size: 12px;
  letter-spacing: 0.02em;
}

.section {
  padding: 64px 0;
  position: relative;
  z-index: 1;
}

.section-alt {
  background: rgba(15, 23, 42, 0.35);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.section-title {
  font-size: 30px;
  letter-spacing: -0.03em;
  text-align: center;
}

.section-sub {
  margin-top: 10px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 700;
  font-size: 14px;
  text-align: center;
  max-width: 80ch;
  margin-left: auto;
  margin-right: auto;
}

.cards {
  margin-top: 26px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.card {
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
}

.card-icon {
  width: 36px;
  height: 36px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.18);
  color: rgba(226, 232, 240, 0.92);
  font-weight: 900;
}

.card h3 {
  margin-top: 12px;
  font-size: 16px;
  letter-spacing: -0.02em;
}

.card p {
  margin-top: 8px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 650;
  font-size: 13px;
  line-height: 1.6;
}

.feature-grid {
  margin-top: 22px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.feature {
  background: rgba(15, 23, 42, 0.58);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 16px;
}

.feature-title {
  font-weight: 950;
  letter-spacing: -0.02em;
}

.feature-text {
  margin-top: 8px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 650;
  font-size: 13px;
  line-height: 1.6;
}

.footer {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.footer-brand {
  font-weight: 950;
}

.footer-muted {
  margin-top: 6px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 700;
  font-size: 13px;
}

.footer-right {
  display: inline-flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (min-width: 900px) {
  .nav-links {
    display: inline-flex;
  }

  .hero-inner {
    grid-template-columns: 1.15fr 0.85fr;
    gap: 34px;
  }

  .hero-copy {
    text-align: left;
    align-items: flex-start;
  }

  .actions {
    justify-content: flex-start;
  }

  .logo-strip {
    justify-content: flex-start;
  }

  .hero-copy h1 {
    font-size: 56px;
  }

  .cards {
    grid-template-columns: repeat(3, 1fr);
  }

  .feature-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>

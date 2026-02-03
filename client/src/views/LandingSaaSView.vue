<template>
  <div class="landing">
    <header class="topbar">
      <div class="container topbar-inner">
        <RouterLink class="brand" to="/" aria-label="CXRaide home">
          <img class="logo" src="@/assets/LOGO2.png" alt="" />
        </RouterLink>

        <nav class="links" aria-label="Primary">
          <a href="#features">Features</a>
          <RouterLink to="/research">Study</RouterLink>
          <RouterLink to="/metrics">Metrics</RouterLink>
          <RouterLink to="/about">About</RouterLink>
        </nav>

        <div class="cta">
          <UiButton variant="ghost" @click="$router.push('/research')">View Study</UiButton>
          <UiButton variant="primary" @click="$router.push('/demo')">Try the Demo</UiButton>
        </div>
      </div>
    </header>

    <main>
      <section class="hero">
        <div class="container hero-inner">
          <div class="copy">
            <UiBadge variant="info">
              <i class="bi bi-shield-check" /> Research demo • Not for clinical diagnosis
            </UiBadge>

            <h1>AI-Assisted Chest X-Ray Annotation &amp; Detection</h1>
            <p class="lead">
              Radiology interpretation can be error-prone under time pressure. CXRaide 2.0 is a lightweight research platform
              to test AI-assisted abnormality detection, expert bounding-box annotation, and structured report generation.
            </p>

            <div class="hero-actions">
              <UiButton variant="primary" size="lg" icon="bi bi-play-circle" @click="$router.push('/demo')">
                Try the Demo
              </UiButton>
              <UiButton variant="secondary" size="lg" icon="bi bi-journal-text" @click="$router.push('/research')">
                View Study
              </UiButton>
            </div>

            <div class="pill-row" style="margin-top: 14px">
              <span class="pill"><i class="bi bi-bounding-box" /> Expert boxes → CSV</span>
              <span class="pill"><i class="bi bi-cpu" /> SSD300_VGG16</span>
              <span class="pill"><i class="bi bi-file-earmark-text" /> Structured report</span>
            </div>
          </div>

          <div class="preview">
            <UiCard title="Demo workspace" subtitle="Upload → predict → verify → export">
              <div class="preview-grid">
                <div class="preview-item">
                  <div class="k">mAP (Iter. 3)</div>
                  <div class="v">31.02%</div>
                </div>
                <div class="preview-item">
                  <div class="k">Recall</div>
                  <div class="v">83.6–91.4%</div>
                </div>
                <div class="preview-item">
                  <div class="k">Artifacts</div>
                  <div class="v">CSV + PDF</div>
                </div>
                <div class="preview-item">
                  <div class="k">Mode</div>
                  <div class="v">Research demo</div>
                </div>
              </div>
              <div class="disclaimer">
                This tool is intended for education and research. Outputs are not validated for clinical use.
              </div>
            </UiCard>
          </div>
        </div>
      </section>

      <section id="features" class="section">
        <div class="container">
          <div class="section-head">
            <h2>Key capabilities</h2>
            <p class="text-muted">A clean, modern workflow for exploring AI-assisted annotation.</p>
          </div>

          <div class="grid-2">
            <UiCard title="Annotation Tool" subtitle="Draw and edit bounding boxes">
              <ul class="list">
                <li>Click-drag to create boxes</li>
                <li>Label abnormalities with color-coded classes</li>
                <li>Export expert annotations to CSV</li>
              </ul>
            </UiCard>
            <UiCard title="AI Detection" subtitle="SSD300_VGG16 predictions">
              <ul class="list">
                <li>Confidence-scored abnormality list</li>
                <li>Toggle Expert vs AI overlays</li>
                <li>Loading states during inference</li>
              </ul>
            </UiCard>
            <UiCard title="Auto Report Generation" subtitle="Structured radiology-style output">
              <ul class="list">
                <li>Findings/Impression template</li>
                <li>Include AI + expert context</li>
                <li>Export as PDF</li>
              </ul>
            </UiCard>
            <UiCard title="Research-backed Model" subtitle="NIH + VinBig + iterative training">
              <ul class="list">
                <li>Dataset description and pipeline</li>
                <li>Iteration comparisons</li>
                <li>Metrics dashboard</li>
              </ul>
            </UiCard>
          </div>

          <div class="bottom-cta">
            <UiButton variant="primary" size="lg" icon="bi bi-play-circle" @click="$router.push('/demo')">
              Try the Demo Workspace
            </UiButton>
          </div>
        </div>
      </section>

      <footer class="footer">
        <div class="container footer-inner">
          <div>
            <div class="foot-brand">CXRaide 2.0</div>
            <div class="text-muted">AI-assisted CXR annotation &amp; detection • Research demo</div>
          </div>
          <div class="footer-links">
            <RouterLink to="/about">About</RouterLink>
            <RouterLink to="/research">Study</RouterLink>
            <RouterLink to="/metrics">Metrics</RouterLink>
          </div>
        </div>
      </footer>
    </main>
  </div>
</template>

<script>
import UiButton from "@/ui/UiButton.vue";
import UiCard from "@/ui/UiCard.vue";
import UiBadge from "@/ui/UiBadge.vue";

export default {
  name: "LandingSaaSView",
  components: { UiButton, UiCard, UiBadge },
};
</script>

<style scoped>
.landing {
  min-height: 100vh;
  background:
    radial-gradient(900px 320px at 20% 0%, rgba(37,99,235,0.10), transparent 55%),
    radial-gradient(900px 360px at 80% 10%, rgba(14,165,233,0.10), transparent 55%),
    var(--bg);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(15,23,42,0.78);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
}

:global(body.theme-light) .topbar {
  background: rgba(255,255,255,0.85);
}

.topbar-inner {
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.brand {
  display: flex;
  align-items: center;
  padding: 6px;
  border-radius: 12px;
}

.brand:hover { background: rgba(30,41,59,0.35); }
:global(body.theme-light) .brand:hover { background: rgba(15,23,42,0.06); }

.logo { height: 26px; width: auto; max-width: 220px; object-fit: contain; display: block; }

.links { display: flex; align-items: center; gap: 14px; color: var(--text-2); }
.links a { color: var(--text-2); font-weight: 600; font-size: 14px; }
.links a:hover { color: var(--primary); text-decoration: none; }

.cta { display: flex; align-items: center; gap: 10px; }

.hero { padding: 48px 0 18px; }
.hero-inner { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 22px; align-items: start; }
@media (max-width: 980px) { .hero-inner { grid-template-columns: 1fr; } }

.copy h1 { font-size: 42px; line-height: 1.06; margin: 14px 0 10px; letter-spacing: -0.02em; }
.lead { color: var(--text-2); font-size: 16px; line-height: 1.55; max-width: 58ch; }

.hero-actions { display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap; }

.pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(30,41,59,0.45);
  color: var(--text-2);
  font-weight: 650;
  font-size: 12.5px;
}

:global(body.theme-light) .pill { background: rgba(255,255,255,0.7); }

.preview-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 12px; }
.preview-item .k { color: var(--muted); font-size: 12px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
.preview-item .v { margin-top: 4px; font-size: 18px; font-weight: 800; color: var(--text); }

.disclaimer { margin-top: 14px; padding: 10px 12px; border-radius: 12px; background: var(--surface-2); color: var(--text-2); font-size: 13px; }

.section { padding: 36px 0 64px; }
.section-head { margin-bottom: 14px; }
.section-head h2 { margin: 0 0 6px; }

#features { scroll-margin-top: 84px; }

.list { margin: 0; padding-left: 18px; color: var(--text-2); line-height: 1.7; }

.bottom-cta { margin-top: 18px; display: flex; justify-content: center; }

.footer { border-top: 1px solid var(--border); padding: 22px 0; background: rgba(15,23,42,0.55); }
:global(body.theme-light) .footer { background: rgba(255,255,255,0.55); }
.footer-inner { display: flex; justify-content: space-between; align-items: center; gap: 14px; flex-wrap: wrap; }
.foot-brand { font-weight: 850; }
.footer-links { display: flex; gap: 14px; }
.footer-links a { color: var(--text-2); font-weight: 650; }
</style>

<template>
  <div class="study">
    <div class="bg" aria-hidden="true">
      <div class="bg-grid" />
      <div class="glow g1" />
      <div class="glow g2" />
    </div>

    <header class="nav">
      <div class="container nav-inner">
        <RouterLink class="brand" to="/">
          <img class="brand-logo" src="@/assets/LOGO1.png" alt="CXRaide" />
        </RouterLink>

        <nav class="nav-links" aria-label="Primary">
          <RouterLink class="nav-link" to="/">Home</RouterLink>
          <a class="nav-link" href="#overview">Overview</a>
          <a class="nav-link" href="#method">Method</a>
          <a class="nav-link" href="#data">Data</a>
          <a class="nav-link" href="#results">Results</a>
          <a class="nav-link" href="#future">Next</a>
        </nav>

        <div class="nav-cta">
          <RouterLink class="nav-link" to="/login">Sign in</RouterLink>
          <RouterLink class="btn btn-primary" to="/login">Try the app</RouterLink>
        </div>
      </div>
    </header>

    <main class="container">
      <section class="hero" aria-labelledby="study-title">
        <div class="hero-copy">
          <div class="badge">
            <span class="badge-dot" />
            <span>Study summary</span>
          </div>

          <h1 id="study-title">Automatic Chest X‑Ray Pattern Annotation and Classification</h1>
          <p class="lead">
            This page distills our paper into a readable summary for both non‑technical readers and computer science
            readers.
          </p>

          <div class="mode" role="tablist" aria-label="Explanation level">
            <button
              class="pill"
              :class="{ active: mode === 'plain' }"
              type="button"
              role="tab"
              :aria-selected="mode === 'plain'"
              @click="mode = 'plain'"
            >
              Plain language
            </button>
            <button
              class="pill"
              :class="{ active: mode === 'tech' }"
              type="button"
              role="tab"
              :aria-selected="mode === 'tech'"
              @click="mode = 'tech'"
            >
              Technical (CS)
            </button>
          </div>

          <div class="quick">
            <div class="quick-item">
              <div class="k">Goal</div>
              <div class="v">Make CXR annotation faster and more consistent, while saving precise bounding boxes.</div>
            </div>
            <div class="quick-item">
              <div class="k">Core model</div>
              <div class="v">SSD300 with a VGG16 backbone (SSD300_VGG16).</div>
            </div>
            <div class="quick-item">
              <div class="k">Data</div>
              <div class="v">NIH + VinBig (preprocessed and balanced across classes).</div>
            </div>
            <div class="quick-item">
              <div class="k">Outputs</div>
              <div class="v">Boxes + labels + a structured radiographic report template.</div>
            </div>
          </div>
        </div>
      </section>

      <section id="overview" class="section">
        <h2>Overview</h2>
        <p v-if="mode === 'plain'">
          Reading chest X‑rays is hard and mistakes can delay treatment. Our study improves CXRaide into a tool that helps
          radiologists and research teams label chest X‑ray abnormalities with bounding boxes, save those labels for later
          review, and generate a clear report format.
        </p>
        <p v-else>
          We present CXRaide 2.0: an end‑to‑end pipeline for chest X‑ray abnormality detection and annotation capture.
          The platform integrates an SSD300_VGG16 detector for localization/classification, persists expert annotations
          (labels + bounding‑box coordinates) for dataset traceability, and produces structured, template‑driven radiology
          text outputs.
        </p>

        <div class="callouts">
          <div class="callout">
            <div class="callout-title">Why it matters</div>
            <div class="callout-text">
              High‑quality bounding boxes are essential for validating AI models, but they are expensive and time‑consuming
              to produce.
            </div>
          </div>
          <div class="callout">
            <div class="callout-title">What we changed in CXRaide 2.0</div>
            <div class="callout-text">
              Saving expert boxes to CSV, improving classification focus, and generating report text from structured
              findings.
            </div>
          </div>
        </div>
      </section>

      <section id="method" class="section section-alt">
        <h2>System workflow</h2>
        <p v-if="mode === 'plain'">
          A typical session is: sign in → upload a chest X‑ray → review AI suggestions → draw or adjust boxes → save your
          annotations → generate a report and download it.
        </p>
        <p v-else>
          The workflow is: authentication → image upload → inference (detector proposes boxes/labels) → expert
          verification/editing → persistence of expert annotations (CSV: image id, class, box coordinates) → report
          generation (templated sections populated by findings + metadata).
        </p>

        <div class="steps">
          <div class="step">
            <div class="step-num">1</div>
            <div>
              <div class="step-title">Upload & infer</div>
              <div class="step-text">Run SSD300_VGG16 to propose abnormality boxes and labels.</div>
            </div>
          </div>
          <div class="step">
            <div class="step-num">2</div>
            <div>
              <div class="step-title">Expert annotate</div>
              <div class="step-text">Draw/edit boxes with zoom and labeling support.</div>
            </div>
          </div>
          <div class="step">
            <div class="step-num">3</div>
            <div>
              <div class="step-title">Save & report</div>
              <div class="step-text">Persist annotations to CSV, then generate a structured report.</div>
            </div>
          </div>
        </div>
      </section>

      <section id="data" class="section">
        <h2>Data and preprocessing</h2>
        <p v-if="mode === 'plain'">
          We combined two public chest X‑ray datasets. We cleaned the data, kept useful images with clear labels, and
          balanced the classes so rare findings are not ignored.
        </p>
        <p v-else>
          We merged NIH and VinBig CXR datasets after filtering and normalization. VinBig annotations were consolidated
          across radiologists (Weighted Box Fusion). Images were resized to 300×300 and annotations were converted to
          Pascal VOC (XML) with train/val splits via stratified sampling; balanced sampling was used to mitigate class
          imbalance.
        </p>

        <div class="grid">
          <div class="feature">
            <div class="feature-title">Sources</div>
            <div class="feature-text">NIH + VinBig public CXR datasets.</div>
          </div>
          <div class="feature">
            <div class="feature-title">Format</div>
            <div class="feature-text">Pascal VOC directory + XML annotations.</div>
          </div>
          <div class="feature">
            <div class="feature-title">Image size</div>
            <div class="feature-text">Resized to 300×300 to match SSD300 input.</div>
          </div>
          <div class="feature">
            <div class="feature-title">Balancing</div>
            <div class="feature-text">Optimized sampling to reduce class imbalance.</div>
          </div>
        </div>
      </section>

      <section id="results" class="section section-alt">
        <h2>Results (high level)</h2>
        <p v-if="mode === 'plain'">
          The model became much better at finding abnormalities (high recall), meaning it usually spots issues that are
          present. However, the exact box placement still needs work (precision drops when we demand very accurate
          localization).
        </p>
        <p v-else>
          Iteration 3 reports moderate mAP (~31.02%) with high recall (~83.6–91.4% depending on size thresholds). Precision
          decreases under stricter IoU thresholds, suggesting bounding‑box regression and localization remain the
          bottlenecks.
        </p>

        <div class="metrics">
          <div class="metric-card">
            <div class="metric-kpi">mAP</div>
            <div class="metric-val">31.02% (Iteration 3)</div>
            <div class="metric-note">AP@[0.50:0.95]</div>
          </div>
          <div class="metric-card">
            <div class="metric-kpi">Recall</div>
            <div class="metric-val">83.6–91.4%</div>
            <div class="metric-note">Small/medium/large AR (Iteration 3)</div>
          </div>
          <div class="metric-card">
            <div class="metric-kpi">Key gap</div>
            <div class="metric-val">Localization</div>
            <div class="metric-note">Precision drops at higher IoU thresholds</div>
          </div>
        </div>
      </section>

      <section id="future" class="section">
        <h2>Limitations and next steps</h2>
        <p v-if="mode === 'plain'">
          Next improvements focus on making the box placement more accurate, reducing false alarms, and producing more
          natural report text.
        </p>
        <p v-else>
          Future work targets (1) improved box regression/localization under stricter IoU, (2) class‑wise calibration and
          reduced background confusion, (3) handling image size inconsistencies, and (4) NLP/LLM‑assisted generation of
          findings text while maintaining clinical structure.
        </p>

        <div class="cta">
          <div>
            <div class="cta-title">Want the full details?</div>
            <div class="cta-text">
              The original PDF is in the repo root as
              <span class="mono">Automatic_Chest_X_Ray_Pattern_Annotation_and_Classification-2.pdf</span>.
            </div>
          </div>
          <RouterLink class="btn btn-primary" to="/login">Open the app</RouterLink>
        </div>
      </section>

      <footer class="footer">
        <div class="footer-left">
          <div class="footer-brand">CXRaide 2.0 · Study</div>
          <div class="footer-muted">Readable summary + technical notes based on our paper.</div>
        </div>
        <div class="footer-right">
          <RouterLink class="nav-link" to="/">Home</RouterLink>
          <RouterLink class="nav-link" to="/login">Sign in</RouterLink>
        </div>
      </footer>
    </main>
  </div>
</template>

<script>
export default {
  name: "StudyView",
  data() {
    return {
      mode: "plain",
    };
  },
};
</script>

<style scoped>
.study {
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
  background-image: radial-gradient(circle at 1px 1px, rgba(148, 163, 184, 0.10) 1px, transparent 0);
  background-size: 42px 42px;
  mask-image: radial-gradient(700px 460px at 50% 10%, rgba(0, 0, 0, 1) 40%, rgba(0, 0, 0, 0) 100%);
  opacity: 0.9;
}

.glow {
  position: absolute;
  width: 680px;
  height: 680px;
  border-radius: 999px;
  filter: blur(60px);
  opacity: 0.22;
}

.g1 {
  left: -220px;
  top: -260px;
  background: radial-gradient(circle at 30% 30%, rgba(59, 130, 246, 1), transparent 60%);
}

.g2 {
  right: -260px;
  top: -180px;
  background: radial-gradient(circle at 30% 30%, rgba(96, 165, 250, 1), transparent 60%);
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
  text-decoration: none;
}

.brand-logo {
  height: 28px;
  width: auto;
  display: block;
}

.nav-links {
  display: none;
  gap: 16px;
}

.nav-link {
  color: rgba(226, 232, 240, 0.72);
  text-decoration: none;
  font-weight: 750;
  font-size: 13px;
}

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
  font-weight: 850;
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

.hero {
  padding: 56px 0 12px;
  position: relative;
  z-index: 1;
}

.hero-copy {
  max-width: 880px;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.10);
  font-weight: 850;
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

h1 {
  margin-top: 14px;
  font-size: 44px;
  line-height: 1.08;
  letter-spacing: -0.04em;
}

.lead {
  margin-top: 12px;
  font-size: 15px;
  line-height: 1.7;
  color: rgba(148, 163, 184, 0.95);
  max-width: 76ch;
}

.mode {
  margin-top: 16px;
  display: inline-flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pill {
  padding: 9px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(15, 23, 42, 0.35);
  color: rgba(226, 232, 240, 0.9);
  font-weight: 850;
  font-size: 12px;
  cursor: pointer;
}

.pill.active {
  border-color: rgba(59, 130, 246, 0.55);
  background: rgba(59, 130, 246, 0.16);
}

.quick {
  margin-top: 18px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.quick-item {
  padding: 14px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.60);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.k {
  font-weight: 900;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.95);
}

.v {
  margin-top: 6px;
  font-weight: 750;
  color: rgba(226, 232, 240, 0.95);
  line-height: 1.55;
}

.section {
  padding: 42px 0;
  position: relative;
  z-index: 1;
}

.section-alt {
  background: rgba(15, 23, 42, 0.35);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

h2 {
  font-size: 26px;
  letter-spacing: -0.03em;
}

p {
  margin-top: 10px;
  color: rgba(148, 163, 184, 0.98);
  font-weight: 650;
  font-size: 14px;
  line-height: 1.75;
  max-width: 90ch;
}

.callouts {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.callout {
  padding: 16px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.58);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.callout-title {
  font-weight: 950;
  letter-spacing: -0.02em;
}

.callout-text {
  margin-top: 8px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 650;
  font-size: 13px;
  line-height: 1.6;
}

.steps {
  margin-top: 14px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.step {
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  gap: 12px;
}

.step-num {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.14);
  border: 1px solid rgba(59, 130, 246, 0.22);
  font-weight: 950;
}

.step-title {
  font-weight: 950;
  letter-spacing: -0.02em;
}

.step-text {
  margin-top: 6px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 650;
  font-size: 13px;
  line-height: 1.6;
}

.grid {
  margin-top: 16px;
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

.metrics {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.metric-card {
  padding: 16px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.metric-kpi {
  font-weight: 950;
  letter-spacing: -0.02em;
  color: rgba(226, 232, 240, 0.95);
}

.metric-val {
  margin-top: 8px;
  font-weight: 950;
  font-size: 18px;
}

.metric-note {
  margin-top: 4px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 700;
  font-size: 12px;
}

.cta {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(11, 18, 32, 0.88);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.14);
}

.cta-title {
  font-weight: 950;
  letter-spacing: -0.02em;
}

.cta-text {
  margin-top: 6px;
  font-weight: 650;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.72);
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.footer {
  padding: 34px 0 60px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
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

  h1 {
    font-size: 54px;
  }

  .quick {
    grid-template-columns: repeat(2, 1fr);
  }

  .callouts {
    grid-template-columns: repeat(2, 1fr);
  }

  .steps {
    grid-template-columns: repeat(3, 1fr);
  }

  .grid {
    grid-template-columns: repeat(4, 1fr);
  }

  .metrics {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>

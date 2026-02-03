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
          <img class="brand-logo" src="@/assets/LOGO1.png" alt="CXRaide" />
        </RouterLink>

        <nav class="nav-links" aria-label="Primary">
          <a href="#features">Features</a>
          <a href="#about">About</a>
          <a href="#process">Process</a>
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
              <span>Paper-backed: annotation + detection + reporting</span>
            </div>

            <h1 id="hero-title">Secure annotation for fast‑moving research teams</h1>
            <p class="lead" v-if="mode === 'plain'">
              CXRaide 2.0 is our research tool for labeling chest X‑rays with bounding boxes, saving those coordinates for
              record‑keeping, and generating a structured radiology-style report.
            </p>
            <p class="lead" v-else>
              CXRaide 2.0 integrates an SSD300_VGG16 detector for abnormality localization/classification, persists
              expert bounding boxes (image + class + coordinates) for dataset traceability, and generates templated
              radiographic text.
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

            <div class="actions">
              <RouterLink class="btn btn-primary" to="/login">Try CXRaide</RouterLink>
              <a class="btn btn-ghost" href="#process">How it works</a>
            </div>

            <div class="logo-strip" aria-label="Designed for">
              <span class="logo-pill">Bounding boxes saved to CSV</span>
              <span class="logo-pill">NIH + VinBig datasets</span>
              <span class="logo-pill">SSD300_VGG16 detector</span>
              <span class="logo-pill">Template-based reports</span>
              <span class="logo-pill">Iterative model training</span>
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
                  <span class="k">Saved</span>
                  <span class="v">CSV · class + box coords</span>
                </div>
                <div class="preview-row">
                  <span class="k">Model</span>
                  <span class="v">IT3 · containerized</span>
                </div>

                <div class="preview-metrics" aria-label="Quality signals">
                  <div class="metric">
                    <div class="metric-name">mAP</div>
                    <div class="metric-bar"><span style="width: 31%" /></div>
                    <div class="metric-val">31%</div>
                  </div>
                  <div class="metric">
                    <div class="metric-name">Recall</div>
                    <div class="metric-bar"><span style="width: 88%" /></div>
                    <div class="metric-val">88%</div>
                  </div>
                </div>

                <div class="preview-note">
                  Iteration 3 shows moderate mAP (~31.02%) and high recall; localization precision drops under stricter
                  IoU thresholds.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" class="section" aria-labelledby="features-title">
        <div class="container">
          <h2 id="features-title" class="section-title">Features</h2>
          <p class="section-sub" v-if="mode === 'plain'">
            CXRaide 2.0 helps teams label chest X‑rays faster while keeping annotations consistent and reusable.
          </p>
          <p class="section-sub" v-else>
            End-to-end pipeline: SSD300_VGG16 detection + expert verification + CSV persistence + template-based reporting.
          </p>

          <div class="split">
            <div>
              <h3 class="kicker">What you get</h3>
              <ul class="bullets" v-if="mode === 'plain'">
                <li>AI suggestions to speed up labeling</li>
                <li>Manual tools to adjust bounding boxes</li>
                <li>Saved coordinates for record-keeping</li>
                <li>Structured report format for clean documentation</li>
              </ul>
              <ul class="bullets" v-else>
                <li>SSD300_VGG16 inference + NMS for candidate boxes</li>
                <li>Expert edits persisted as (image, class, bbox coords) in CSV</li>
                <li>Dataset-friendly preprocessing (e.g., stratified sampling, balancing)</li>
                <li>Template-driven Findings/Impression report output</li>
              </ul>

              <div class="mini-strip" aria-label="Key elements">
                <span class="mini">Bounding boxes</span>
                <span class="mini">CSV exports</span>
                <span class="mini">Public datasets</span>
                <span class="mini">Report templates</span>
              </div>
            </div>

            <div class="panel">
              <div class="panel-title">Study objectives (condensed)</div>
              <div class="panel-grid">
                <div class="panel-item">
                  <div class="panel-k">Persist annotations</div>
                  <div class="panel-v">Save expert labels + coordinates for later validation and reuse.</div>
                </div>
                <div class="panel-item">
                  <div class="panel-k">Improve classification focus</div>
                  <div class="panel-v">Reduce mislabels and avoid irrelevant background detections.</div>
                </div>
                <div class="panel-item">
                  <div class="panel-k">Standardize reporting</div>
                  <div class="panel-v">Generate consistent report sections with clear locations.</div>
                </div>
                <div class="panel-item">
                  <div class="panel-k">Iterate and measure</div>
                  <div class="panel-v">Track AP/AR and refine across training iterations.</div>
                </div>
              </div>
            </div>
          </div>

          <div class="stats" aria-label="Key results">
            <div class="stat">
              <div class="stat-k">mAP (Iter. 3)</div>
              <div class="stat-v">31.02%</div>
              <div class="stat-m">AP@[0.50:0.95]</div>
            </div>
            <div class="stat">
              <div class="stat-k">Recall</div>
              <div class="stat-v">83.6–91.4%</div>
              <div class="stat-m">AR by object size</div>
            </div>
            <div class="stat">
              <div class="stat-k">Main bottleneck</div>
              <div class="stat-v">Localization</div>
              <div class="stat-m">Precision drops at stricter IoU</div>
            </div>
          </div>
        </div>
      </section>

      <section id="about" class="section section-alt" aria-labelledby="about-title">
        <div class="container">
          <h2 id="about-title" class="section-title">About the study</h2>
          <p class="section-sub" v-if="mode === 'plain'">
            Our paper focuses on three things: saving radiologist annotations, improving abnormality detection, and generating
            structured reports.
          </p>
          <p class="section-sub" v-else>
            The study extends prior CXRaide work by persisting expert bounding boxes, improving detection quality, and producing
            templated radiographic outputs.
          </p>

          <div class="about-grid">
            <div>
              <h3 class="kicker">Abstract, simplified</h3>
              <p class="body" v-if="mode === 'plain'">
                Chest X‑ray interpretation errors can delay treatment. Many AI studies struggle because expert boxes are not stored
                consistently with coordinates. CXRaide 2.0 improves the labeling workflow by saving bounding box coordinates,
                supporting AI-assisted detection, and producing structured reports.
              </p>
              <p class="body" v-else>
                We implement an AI-assisted annotation platform backed by SSD300_VGG16. The system captures expert box coordinates
                (CSV) to enable traceable evaluation, uses balanced/stratified dataset preparation, and generates report text using
                a template-driven approach.
              </p>

              <h3 class="kicker">Key technical choices</h3>
              <dl class="dl">
                <div>
                  <dt>Detector</dt>
                  <dd>SSD300_VGG16 (VGG16 backbone)</dd>
                </div>
                <div>
                  <dt>Losses</dt>
                  <dd>Focal loss (class) + Smooth L1 (boxes)</dd>
                </div>
                <div>
                  <dt>Data</dt>
                  <dd>NIH + VinBig; WBF for multi-annotator consolidation</dd>
                </div>
                <div>
                  <dt>Format</dt>
                  <dd>Pascal VOC-style preprocessing; resize to 300×300</dd>
                </div>
              </dl>
            </div>

            <div class="aside">
              <div class="aside-title">Objectives</div>
              <ol class="objectives">
                <li>Save expert annotations (class + bounding box coordinates) for record‑keeping</li>
                <li>Improve abnormality classification and reduce background detections</li>
                <li>Generate structured radiographic reports with clear locations</li>
              </ol>

              <div class="aside-note" v-if="mode === 'plain'">
                In short: faster labeling today, better datasets tomorrow.
              </div>
              <div class="aside-note" v-else>
                In short: improved dataset governance + measurable model iteration.
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="process" class="section" aria-labelledby="process-title">
        <div class="container">
          <h2 id="process-title" class="section-title">Process</h2>
          <p class="section-sub" v-if="mode === 'plain'">
            A simple flow from upload to saved annotations and a downloadable report.
          </p>
          <p class="section-sub" v-else>
            Auth → upload → inference → expert edits → persist → report generation.
          </p>

          <ol class="timeline" aria-label="Workflow timeline">
            <li>
              <div class="t-dot" />
              <div class="t-body">
                <div class="t-title">Upload a CXR</div>
                <div class="t-text">Start a case and attach an image for review.</div>
              </div>
            </li>
            <li>
              <div class="t-dot" />
              <div class="t-body">
                <div class="t-title">AI suggests boxes + labels</div>
                <div class="t-text" v-if="mode === 'plain'">The tool highlights likely findings to speed you up.</div>
                <div class="t-text" v-else>SSD300_VGG16 proposes candidate detections; NMS reduces duplicates.</div>
              </div>
            </li>
            <li>
              <div class="t-dot" />
              <div class="t-body">
                <div class="t-title">Expert draws/adjusts</div>
                <div class="t-text">Zoom, label, refine boxes until the annotation is correct.</div>
              </div>
            </li>
            <li>
              <div class="t-dot" />
              <div class="t-body">
                <div class="t-title">Save annotations</div>
                <div class="t-text" v-if="mode === 'plain'">Coordinates are saved so nothing gets lost.</div>
                <div class="t-text" v-else>Persist (image id, class, bbox coords) to CSV for traceability.</div>
              </div>
            </li>
            <li>
              <div class="t-dot" />
              <div class="t-body">
                <div class="t-title">Generate report</div>
                <div class="t-text" v-if="mode === 'plain'">Get a clean, consistent report layout.</div>
                <div class="t-text" v-else>Template-based report sections (Findings/Impression) populated from labels.</div>
              </div>
            </li>
          </ol>

          <div class="faq" aria-label="Common questions">
            <details>
              <summary>Why do you save bounding boxes to CSV?</summary>
              <p>So annotations are reusable for validation, benchmarking, and training — not trapped in screenshots.</p>
            </details>
            <details>
              <summary>Why is localization the bottleneck?</summary>
              <p>High recall can still come with imperfect box placement; stricter IoU thresholds expose that gap.</p>
            </details>
            <details>
              <summary>What’s next after this study?</summary>
              <p>Better box regression, improved class calibration, and more natural report text via NLP — while keeping structure.</p>
            </details>
          </div>
        </div>
      </section>

      <section id="contact" class="section section-alt" aria-labelledby="contact-title">
        <div class="container">
          <h2 id="contact-title" class="section-title">Contact</h2>
          <p class="section-sub" v-if="mode === 'plain'">
            Want to use CXRaide 2.0 for your labeling workflow? Reach out and we’ll help you get set up.
          </p>
          <p class="section-sub" v-else>
            For deployments, dataset workflows, or evaluation protocols, contact the team for onboarding and collaboration.
          </p>

          <div class="contact-split">
            <div class="cta-band">
              <div>
                <div class="cta-title">Try it locally</div>
                <div class="cta-text">Use Docker for a stable dev environment and iterate quickly.</div>
              </div>
              <RouterLink class="btn btn-primary" to="/login">Open the app</RouterLink>
            </div>

            <div class="contact-card">
              <div class="contact-title">Next steps</div>
              <ul class="bullets" v-if="mode === 'plain'">
                <li>Make boxes more accurate</li>
                <li>Reduce false alarms</li>
                <li>Improve report wording while keeping structure</li>
              </ul>
              <ul class="bullets" v-else>
                <li>Improve box regression and localization under higher IoU</li>
                <li>Class-wise calibration and background suppression</li>
                <li>NLP/LLM-assisted report generation with templated constraints</li>
              </ul>
            </div>
          </div>

          <div class="footer">
            <div class="footer-left">
              <div class="footer-brand">CXRaide 2.0</div>
              <div class="footer-muted">Automatic chest X‑ray pattern annotation and classification.</div>
            </div>
            <div class="footer-right">
              <RouterLink class="nav-link" to="/login">Sign in</RouterLink>
              <a class="nav-link" href="#features">Features</a>
              <a class="nav-link" href="#about">About</a>
              <a class="nav-link" href="#process">Process</a>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
export default {
  name: "LandingView",
  data() {
    return {
      mode: "plain",
    };
  },
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

.mode {
  margin-top: 16px;
  display: inline-flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
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

.kicker {
  margin-top: 0;
  font-weight: 950;
  letter-spacing: -0.02em;
  font-size: 14px;
  color: rgba(226, 232, 240, 0.92);
}

.body {
  margin-top: 10px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 650;
  font-size: 13px;
  line-height: 1.7;
}

.split {
  margin-top: 26px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  align-items: start;
}

.bullets {
  margin: 12px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.bullets li {
  position: relative;
  padding-left: 18px;
  color: rgba(148, 163, 184, 0.98);
  font-weight: 700;
  font-size: 13px;
  line-height: 1.55;
}

.bullets li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 9px;
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: rgba(96, 165, 250, 0.95);
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.14);
}

.mini-strip {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.mini {
  padding: 9px 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.40);
  border: 1px solid rgba(255, 255, 255, 0.10);
  color: rgba(148, 163, 184, 0.95);
  font-weight: 900;
  font-size: 12px;
  letter-spacing: 0.02em;
}

.panel {
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.10);
  padding: 16px;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.22);
}

.panel-title {
  font-weight: 950;
  letter-spacing: -0.02em;
}

.panel-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.panel-item {
  padding: 12px;
  border-radius: 14px;
  background: rgba(2, 6, 23, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.panel-k {
  font-weight: 950;
  letter-spacing: -0.02em;
  font-size: 13px;
}

.panel-v {
  margin-top: 6px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 650;
  font-size: 12.5px;
  line-height: 1.55;
}

.stats {
  margin-top: 18px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.stat {
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 14px;
}

.stat-k {
  color: rgba(148, 163, 184, 0.95);
  font-weight: 900;
  font-size: 12px;
}

.stat-v {
  margin-top: 6px;
  font-weight: 950;
  font-size: 22px;
  letter-spacing: -0.02em;
}

.stat-m {
  margin-top: 2px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 700;
  font-size: 12px;
}

.about-grid {
  margin-top: 22px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  align-items: start;
}

.dl {
  margin-top: 12px;
  display: grid;
  gap: 10px;
}

.dl > div {
  padding: 12px;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.50);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dl dt {
  font-weight: 950;
  font-size: 12px;
  color: rgba(226, 232, 240, 0.92);
}

.dl dd {
  margin: 6px 0 0;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 700;
  font-size: 12.5px;
  line-height: 1.55;
}

.aside {
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.10);
  padding: 16px;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.22);
}

.aside-title {
  font-weight: 950;
  letter-spacing: -0.02em;
}

.objectives {
  margin: 12px 0 0;
  padding-left: 18px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 700;
  font-size: 13px;
  line-height: 1.65;
}

.aside-note {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(226, 232, 240, 0.86);
  font-weight: 850;
  font-size: 12.5px;
}

.timeline {
  margin: 22px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 14px;
}

.timeline li {
  display: grid;
  grid-template-columns: 16px 1fr;
  gap: 12px;
  align-items: start;
  padding: 14px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.t-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: rgba(96, 165, 250, 0.95);
  box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.14);
  margin-top: 4px;
}

.t-title {
  font-weight: 950;
  letter-spacing: -0.02em;
}

.t-text {
  margin-top: 6px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 650;
  font-size: 13px;
  line-height: 1.6;
}

.faq {
  margin-top: 18px;
  display: grid;
  gap: 10px;
}

.faq details {
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.50);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 14px;
}

.faq summary {
  cursor: pointer;
  font-weight: 950;
  letter-spacing: -0.02em;
  color: rgba(226, 232, 240, 0.92);
}

.faq p {
  margin-top: 10px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 650;
  font-size: 13px;
  line-height: 1.65;
}

.contact-split {
  margin-top: 22px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.cta-band {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.10);
}

.cta-title {
  font-weight: 950;
  letter-spacing: -0.02em;
}

.cta-text {
  margin-top: 6px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 650;
  font-size: 13px;
  line-height: 1.55;
}

.contact-card {
  padding: 16px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.contact-title {
  font-weight: 950;
  letter-spacing: -0.02em;
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
  margin-top: 26px;
  padding-top: 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.footer-left {
  min-width: 220px;
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

  .mode {
    justify-content: flex-start;
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

  .split {
    grid-template-columns: 1.05fr 0.95fr;
    gap: 18px;
  }

  .panel-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats {
    grid-template-columns: repeat(3, 1fr);
  }

  .about-grid {
    grid-template-columns: 1.2fr 0.8fr;
    gap: 18px;
  }

  .contact-split {
    grid-template-columns: 1.1fr 0.9fr;
    gap: 14px;
    align-items: stretch;
  }

  .cards {
    grid-template-columns: repeat(3, 1fr);
  }

  .feature-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>

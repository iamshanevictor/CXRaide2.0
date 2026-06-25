<template>
  <div class="landing">
    <header class="topbar">
      <div class="container topbar-inner">
        <RouterLink class="brand" to="/" aria-label="CXRaide home">
          <img class="logo" src="@/assets/LOGO2.png" alt="" />
        </RouterLink>

        <nav class="links" aria-label="Primary">
          <a href="#features">Overview</a>
          <RouterLink to="/research">Study</RouterLink>
          <RouterLink to="/metrics">Metrics</RouterLink>
          <RouterLink to="/about">About</RouterLink>
        </nav>

        <div class="cta">
          <UiButton variant="ghost" @click="$router.push('/research')">View Study</UiButton>
          <UiButton variant="primary" @click="$router.push('/demo')">Open Prototype</UiButton>
        </div>
      </div>
    </header>

    <main>
      <section class="hero">
        <div class="container hero-inner">
          <div class="copy">
            <UiBadge variant="info">
              <i class="bi bi-shield-check" /> Research prototype - Not for clinical diagnosis
            </UiBadge>

            <h1>CXRaide 2.0: AI-Assisted Chest X-Ray Annotation and Abnormality Detection</h1>
            <p class="lead">
              A PCSC 2025 research prototype for studying human-in-the-loop chest X-ray workflows:
              AI-assisted abnormality localization, expert bounding-box annotation, annotation preservation,
              and template-based structured report generation.
            </p>

            <div class="hero-actions">
              <UiButton variant="primary" size="lg" icon="bi bi-journal-text" @click="$router.push('/research')">
                Read the Study
              </UiButton>
              <UiButton variant="secondary" size="lg" icon="bi bi-graph-up" @click="$router.push('/metrics')">
                View Results
              </UiButton>
            </div>

            <div class="pill-row" style="margin-top: 14px">
              <span class="pill"><i class="bi bi-cpu" /> SSD300_VGG16</span>
              <span class="pill"><i class="bi bi-bounding-box" /> Bounding boxes to CSV</span>
              <span class="pill"><i class="bi bi-file-earmark-medical" /> Template reports</span>
              <span class="pill"><i class="bi bi-people" /> Expert review required</span>
            </div>
          </div>

          <div class="preview">
            <UiCard title="Research Snapshot" subtitle="Philippine Computing Science Congress 2025">
              <div class="preview-grid">
                <div class="preview-item">
                  <div class="k">Status</div>
                  <div class="v">Research Prototype</div>
                </div>
                <div class="preview-item">
                  <div class="k">mAP</div>
                  <div class="v">31.02%</div>
                </div>
                <div class="preview-item">
                  <div class="k">Recall</div>
                  <div class="v">83.6-91.4%</div>
                </div>
                <div class="preview-item">
                  <div class="k">Average AUC</div>
                  <div class="v">~0.82</div>
                </div>
              </div>
              <div class="disclaimer">
                Research prototype for educational and research purposes only. Outputs are not clinically validated
                and should not be used for medical diagnosis.
              </div>
            </UiCard>
          </div>
        </div>
      </section>

      <section id="features" class="section">
        <div class="container">
          <div class="section-head">
            <h2>What the study addresses</h2>
            <p class="text-muted">
              Chest X-ray interpretation is high-volume and time-sensitive. CXRaide 2.0 focuses on preserving
              expert annotations and supporting reproducible AI-assisted evaluation.
            </p>
          </div>

          <div class="grid-2">
            <UiCard title="Research Problem" subtitle="Annotation, validation, and reproducibility">
              <p class="p">
                Manual abnormality annotation requires expert radiologists and can be expensive, time-consuming,
                and inconsistent. Many systems classify abnormalities but do not adequately preserve expert
                bounding-box coordinates needed for validation and future AI training.
              </p>
            </UiCard>
            <UiCard title="Human-in-the-loop Workflow" subtitle="AI suggestions remain subject to expert review">
              <ul class="list">
                <li>AI provides initial predictions and confidence scores.</li>
                <li>Radiologists review, verify, and refine bounding boxes.</li>
                <li>Expert-created labels and coordinates are saved for later analysis.</li>
              </ul>
            </UiCard>
            <UiCard title="Core Capabilities" subtitle="One research environment">
              <ul class="list">
                <li>AI-assisted abnormality detection and localization.</li>
                <li>Manual box creation, editing, zoom support, and labeling.</li>
                <li>CSV annotation export and PDF report export.</li>
              </ul>
            </UiCard>
            <UiCard title="Structured Reporting" subtitle="Template-based, research-only output">
              <ul class="list">
                <li>Clinical Indication, Findings, Impression, and Recommendations sections.</li>
                <li>RSNA RadReport-inspired templates for consistent documentation.</li>
                <li>Not a substitute for professional medical interpretation.</li>
              </ul>
            </UiCard>
          </div>

          <div class="bottom-cta">
            <UiButton variant="primary" size="lg" icon="bi bi-play-circle" @click="$router.push('/demo')">
              Open Prototype Workspace
            </UiButton>
          </div>
        </div>
      </section>

      <section class="research-fill">
        <div class="container">
          <div class="section-head compact-head">
            <h2>Research workflow</h2>
            <p class="text-muted">
              The prototype combines model inference, expert annotation, coordinate preservation, and structured export.
            </p>
          </div>

          <div class="info-grid timeline-grid">
            <div v-for="step in workflow" :key="step.label" class="info-tile">
              <div class="info-kicker">Step {{ step.index }}</div>
              <h3>{{ step.label }}</h3>
              <p>{{ step.detail }}</p>
            </div>
          </div>

          <div class="section-head compact-head tag-head">
            <h2>Detected abnormalities</h2>
            <p class="text-muted">
              CXRaide 2.0 supports nine chest X-ray abnormality categories used in the research prototype.
            </p>
          </div>

          <div class="tag-panel">
            <span v-for="item in abnormalities" :key="item" class="tag">
              <i class="bi bi-dot" /> {{ item }}
            </span>
          </div>
        </div>
      </section>

      <footer class="footer">
        <div class="container footer-inner">
          <div>
            <div class="foot-brand">CXRaide 2.0</div>
            <div class="text-muted">AI-assisted CXR annotation and detection - PCSC 2025 research prototype</div>
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
  data() {
    return {
      workflow: [
        { index: "1", label: "Upload Chest X-Ray", detail: "A chest X-ray image is loaded into the research workspace." },
        { index: "2", label: "AI Detection", detail: "SSD300_VGG16 proposes abnormality labels, confidence scores, and boxes." },
        { index: "3", label: "Expert Review", detail: "A radiologist verifies, edits, or adds abnormality annotations." },
        { index: "4", label: "Save Coordinates", detail: "Filename, abnormality label, and bounding-box coordinates are preserved." },
        { index: "5", label: "Generate Report", detail: "A structured radiology-style report is created from reviewed findings." },
        { index: "6", label: "Export Results", detail: "Reviewed annotations and reports are exported as CSV and PDF." },
      ],
      abnormalities: [
        "Cardiomegaly",
        "Pleural Thickening",
        "Pulmonary Fibrosis",
        "Pleural Effusion",
        "Nodule / Mass",
        "Infiltration",
        "Consolidation",
        "Atelectasis",
        "Pneumothorax",
      ],
    };
  },
};
</script>

<style scoped>
.landing {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(900px 320px at 20% 0%, rgba(37,99,235,0.10), transparent 55%),
    radial-gradient(900px 360px at 80% 10%, rgba(14,165,233,0.10), transparent 55%),
    var(--bg);
}

main {
  flex: 1;
  display: flex;
  flex-direction: column;
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
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.brand {
  display: flex;
  align-items: center;
  padding: 4px;
  border-radius: 8px;
}

.brand:hover { background: rgba(30,41,59,0.35); }
:global(body.theme-light) .brand:hover { background: rgba(15,23,42,0.06); }

.logo { height: 22px; width: auto; max-width: 190px; object-fit: contain; display: block; }

.links { display: flex; align-items: center; gap: 10px; color: var(--text-2); }
.links a { color: var(--text-2); font-weight: 600; font-size: 13px; }
.links a:hover { color: var(--primary); text-decoration: none; }

.cta { display: flex; align-items: center; gap: 6px; }

.hero { padding: 34px 0 18px; }
.hero-inner { display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 22px; align-items: start; }
@media (max-width: 980px) { .hero-inner { grid-template-columns: 1fr; } }

.copy h1 { font-size: 34px; line-height: 1.12; margin: 12px 0 9px; letter-spacing: -0.01em; }
.lead { color: var(--text-2); font-size: 14px; line-height: 1.52; max-width: 68ch; }

.hero-actions { display: flex; gap: 10px; margin-top: 14px; flex-wrap: wrap; }

.pill,
.tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 9px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(30,41,59,0.45);
  color: var(--text-2);
  font-weight: 650;
  font-size: 12px;
}

:global(body.theme-light) .pill,
:global(body.theme-light) .tag { background: rgba(255,255,255,0.7); }

.preview-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 10px; }
.preview-item .k { color: var(--muted); font-size: 11px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
.preview-item .v { margin-top: 3px; font-size: 16px; font-weight: 800; color: var(--text); }

.disclaimer { margin-top: 10px; padding: 8px 10px; border-radius: 8px; background: var(--surface-2); color: var(--text-2); font-size: 12px; }

.section { padding: 24px 0 18px; }
.section-head { margin-bottom: 12px; }
.section-head h2 { margin: 0 0 5px; font-size: 20px; }

#features { scroll-margin-top: 66px; }

.p { margin: 0; color: var(--text-2); line-height: 1.55; font-size: 13px; }
.list { margin: 0; padding-left: 17px; color: var(--text-2); line-height: 1.55; font-size: 13px; }

.bottom-cta { margin-top: 14px; display: flex; justify-content: center; }

.research-fill {
  padding: 18px 0 36px;
}

.compact-head {
  max-width: 780px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.timeline-grid {
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.info-tile {
  min-height: 138px;
  padding: 13px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: rgba(15, 23, 42, 0.62);
}

.info-kicker {
  color: var(--primary-2);
  font-size: 11px;
  font-weight: 750;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.info-tile h3 {
  margin: 6px 0 6px;
  color: var(--text);
  font-size: 14px;
}

.info-tile p {
  margin: 0;
  color: var(--text-2);
  font-size: 12.5px;
  line-height: 1.48;
}

@media (max-width: 1100px) {
  .info-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .timeline-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (max-width: 640px) {
  .info-grid { grid-template-columns: 1fr; }
  .timeline-grid { grid-template-columns: 1fr; }
}

.tag-head {
  margin-top: 18px;
}

.tag-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: rgba(15, 23, 42, 0.62);
}

.footer { margin-top: auto; border-top: 1px solid var(--border); padding: 16px 0; background: rgba(15,23,42,0.55); }
:global(body.theme-light) .footer { background: rgba(255,255,255,0.55); }
.footer-inner { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; }
.foot-brand { font-weight: 850; }
.footer-links { display: flex; gap: 10px; }
.footer-links a { color: var(--text-2); font-weight: 650; }
</style>


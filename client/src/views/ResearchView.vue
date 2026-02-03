<template>
  <div class="page">
    <div class="content">
      <div class="container" style="padding: 18px 0 34px">
        <div class="page-head">
          <h1>Research / Study : <span class="highlight">CXRaide 2.0</span></h1>
        </div>

        <UiBadge variant="warning" style="margin-bottom: 12px">
          <i class="bi bi-exclamation-triangle" /> Research demo • Not for clinical diagnosis
        </UiBadge>

        <div class="grid-2">
          <UiCard title="Overview" subtitle="Problem → tool → evaluation">
            <p class="p">
              Chest X-rays are high-volume and time-sensitive. Interpretation errors can delay care.
              CXRaide 2.0 explores an AI-assisted workflow: model suggestions + expert verification + traceable exports.
            </p>
            <ul class="list">
              <li>Expert bounding boxes saved to CSV</li>
              <li>AI abnormality detection (SSD300_VGG16)</li>
              <li>Structured report generation for standardized output</li>
            </ul>
          </UiCard>

          <UiCard title="How it works" subtitle="Pipeline at a glance">
            <div class="pipeline">
              <div class="step"><span class="num">1</span><span>Upload CXR</span></div>
              <i class="bi bi-arrow-right" />
              <div class="step"><span class="num">2</span><span>Run detection</span></div>
              <i class="bi bi-arrow-right" />
              <div class="step"><span class="num">3</span><span>Expert edits</span></div>
              <i class="bi bi-arrow-right" />
              <div class="step"><span class="num">4</span><span>Export CSV/PDF</span></div>
            </div>
            <div class="text-muted" style="margin-top: 10px; font-size: 13px; line-height: 1.45;">
              The goal is to make labeling and analysis reproducible: every box has coordinates, labels, and provenance.
            </div>
          </UiCard>
        </div>

        <div class="grid-2" style="margin-top: 16px">
          <UiCard title="Dataset" subtitle="NIH + VinBig">
            <ul class="list">
              <li>NIH ChestX-ray14 + VinBig used for training/evaluation</li>
              <li>Preprocessing: resize to detector input, normalization</li>
              <li>Sampling/balancing strategies to address class imbalance</li>
            </ul>
          </UiCard>

          <UiCard title="Model architecture" subtitle="SSD300_VGG16">
            <ul class="list">
              <li>Single-shot detector with VGG16 backbone</li>
              <li>Bounding box regression + classification heads</li>
              <li>Postprocessing: confidence thresholding + NMS</li>
            </ul>
          </UiCard>

          <UiCard title="Metrics" subtitle="What we track">
            <ul class="list">
              <li>mAP (AP@[0.50:0.95]) for detection quality</li>
              <li>Precision/Recall for sensitivity vs specificity</li>
              <li>AUC per abnormality (where applicable)</li>
            </ul>
          </UiCard>

          <UiCard title="Iterations" subtitle="Comparison across training rounds">
            <p class="p">
              Iterations are compared to measure improvements and failure modes (e.g., localization vs classification).
            </p>
            <div class="pill-row">
              <span class="pill">IT2: SSD300_VGG16-CXR9</span>
              <span class="pill">IT3: SSD300_VGG16-CXR6plus3</span>
            </div>
            <div style="margin-top: 12px">
              <UiButton variant="secondary" icon="bi bi-graph-up" @click="$router.push('/metrics')">Open metrics dashboard</UiButton>
            </div>
          </UiCard>
        </div>

        <UiCard title="Screenshots / diagrams" subtitle="(placeholders)" style="margin-top: 16px">
          <div class="shots">
            <div class="shot">Add: workspace screenshot</div>
            <div class="shot">Add: model diagram</div>
            <div class="shot">Add: metrics chart</div>
          </div>
        </UiCard>
      </div>
    </div>
  </div>
</template>

<script>
import UiCard from "@/ui/UiCard.vue";
import UiButton from "@/ui/UiButton.vue";
import UiBadge from "@/ui/UiBadge.vue";

export default {
  name: "ResearchView",
  components: { UiCard, UiButton, UiBadge },
};
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); }
.content { background: var(--bg); }

.page-head {
  margin-bottom: 14px;
  padding: 10px 2px 0;
}

.page-head h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.01em;
}

.p { margin: 0 0 10px; color: var(--text-2); line-height: 1.55; }
.list { margin: 0; padding-left: 18px; color: var(--text-2); line-height: 1.7; }

.pipeline {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.step {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 14px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  font-weight: 700;
  color: var(--text);
}

.num {
  width: 28px;
  height: 28px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: var(--primary-soft);
  color: var(--primary);
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-2);
  font-weight: 650;
  font-size: 12.5px;
}

.shots { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px; }
@media (max-width: 980px) { .shots { grid-template-columns: 1fr; } }

.shot {
  height: 140px;
  border-radius: 16px;
  border: 1px dashed rgba(37,99,235,0.45);
  background: radial-gradient(500px 140px at 20% 0%, rgba(37,99,235,0.08), transparent 60%), var(--surface);
  display: grid;
  place-items: center;
  color: var(--muted);
  font-weight: 700;
}
</style>

<template>
  <div class="page">
    <div class="container" style="padding: 18px 0 34px">
      <div class="page-head">
        <h1>Results / Metrics : <span class="highlight">Dashboard</span></h1>
      </div>

      <div class="grid-3">
        <UiCard title="mAP" subtitle="Mean Average Precision (AP@[0.50:0.95])">
          <div class="big">31.02%</div>
          <div class="text-muted">Iteration 3 final performance</div>
          <div class="metric-help">
            mAP aggregates detection quality across IoU thresholds (0.50 → 0.95). A prediction only counts as correct when the predicted bounding box overlaps the ground-truth box by at least the threshold IoU; averaging across thresholds rewards both finding the abnormality and localizing it precisely.
          </div>
        </UiCard>
        <UiCard title="Recall" subtitle="Average Recall">
          <div class="big">83.6–91.4%</div>
          <div class="text-muted">Across area sizes (Iteration 3)</div>
          <div class="metric-help" aria-live="polite">
            Recall is the fraction of ground-truth abnormalities that the model detects (i.e., produces a matching prediction). The displayed range reflects that smaller vs. larger abnormalities are detected with different success rates—higher recall means fewer missed findings.
          </div>
        </UiCard>
        <UiCard title="AUC" subtitle="Average AUC (per abnormality)">
          <div class="big">~0.82</div>
          <div class="text-muted">Model discrimination signal (Iteration 3)</div>
          <div class="metric-help" aria-live="polite">
            AUC (Area Under the ROC Curve) summarizes how well the model ranks abnormal vs. normal instances across all decision thresholds. An AUC near 1.0 indicates strong separation (good discrimination); ~0.82 suggests the model reliably assigns higher scores to true abnormalities than to non-abnormal findings, though not perfectly.
          </div>
        </UiCard>

      </div>

      <div class="grid-2" style="margin-top: 16px">
        <UiCard title="Iteration comparison" subtitle="mAP improves over training iterations">
          <ChartCanvas :config="iterationConfig" />
        </UiCard>

        <UiCard title="Class performance" subtitle="AUC per abnormality (higher = better separation)">
          <ChartCanvas :config="aucConfig" />
        </UiCard>
      </div>

      <div class="grid-2" style="margin-top: 16px">
        <UiCard title="Precision/Recall" subtitle="Tradeoff (demo)">
          <ChartCanvas :config="prConfig" />
        </UiCard>

        <UiCard title="Notes" subtitle="How to interpret the charts">
          <ul class="list">
            <li>
              <strong>Iteration comparison (mAP):</strong> mAP rises when the model both finds more true abnormalities (recall) and produces tighter boxes (better localization). The jump to Iteration 3 indicates a larger fraction of predictions pass the stricter overlap requirements.
            </li>
            <li>
              <strong>AUC by abnormality:</strong> each bar is the model’s ranking ability for that abnormality. Higher AUC means the model scores true cases above non-cases across many possible decision thresholds.
            </li>
            <li>
              <strong>Precision/Recall tradeoff:</strong> as confidence threshold increases, precision typically increases (fewer false positives) while recall may decrease (more missed findings). Choose a threshold based on the cost of missing vs. over-calling.
            </li>
          </ul>
          <div style="margin-top: 12px">
            <UiButton variant="primary" icon="bi bi-play-circle" @click="$router.push('/demo')">Open demo workspace</UiButton>
          </div>
        </UiCard>
      </div>
    </div>
  </div>
</template>

<script>
import UiCard from "@/ui/UiCard.vue";
import UiButton from "@/ui/UiButton.vue";
import ChartCanvas from "@/components/charts/ChartCanvas.vue";

export default {
  name: "MetricsDashboardView",
  components: { UiCard, UiButton, ChartCanvas },
  computed: {
    iterationConfig() {
      return {
        type: "line",
        data: {
          labels: ["Iteration 1", "Iteration 2", "Iteration 3"],
          datasets: [
            {
              label: "mAP (AP@[0.50:0.95])",
              data: [0.0092, 0.0079, 0.3102],
              tension: 0.35,
              borderColor: "#2563eb",
              backgroundColor: "rgba(37,99,235,0.10)",
              fill: true,
              pointRadius: 4,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: true },
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { callback: (v) => `${Math.round(v * 100)}%` },
            },
          },
        },
      };
    },
    aucConfig() {
      return {
        type: "bar",
        data: {
          labels: ["Cardiomegaly", "Effusion", "Nodule/Mass", "Infiltration"],
          datasets: [
            {
              label: "AUC",
              data: [0.86, 0.81, 0.79, 0.82],
              backgroundColor: [
                "rgba(220,38,38,0.28)",
                "rgba(217,119,6,0.28)",
                "rgba(37,99,235,0.28)",
                "rgba(22,163,74,0.28)",
              ],
              borderColor: ["#dc2626", "#d97706", "#2563eb", "#16a34a"],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            y: { suggestedMin: 0.5, suggestedMax: 1.0 },
          },
        },
      };
    },
    prConfig() {
      return {
        type: "line",
        data: {
          labels: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
          datasets: [
            {
              label: "Precision",
              data: [0.78, 0.76, 0.73, 0.70, 0.66, 0.62, 0.57, 0.49, 0.41],
              borderColor: "#2563eb",
              tension: 0.3,
              pointRadius: 0,
            },
            {
              label: "Recall",
              data: [0.34, 0.44, 0.55, 0.63, 0.72, 0.80, 0.86, 0.90, 0.92],
              borderColor: "#16a34a",
              tension: 0.3,
              pointRadius: 0,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: true } },
          scales: {
            x: { title: { display: true, text: "Confidence threshold" } },
            y: { beginAtZero: true, suggestedMax: 1.0 },
          },
        },
      };
    },
  },
};
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); }

.page-head {
  margin-bottom: 8px;
  padding: 6px 2px 0;
}

.page-head h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.01em;
}

.highlight { color: var(--primary); }

.list { margin: 0; padding-left: 15px; color: var(--text-2); line-height: 1.45; font-size: 12px; }

.big { font-size: 24px; font-weight: 900; letter-spacing: -0.01em; color: var(--text); }
</style>

<style scoped>
.page { min-height: 100vh; background: var(--bg); }
.big { font-size: 24px; font-weight: 900; letter-spacing: -0.01em; color: var(--text); }
.list { margin: 0; padding-left: 15px; color: var(--text-2); line-height: 1.45; font-size: 12px; }
</style>

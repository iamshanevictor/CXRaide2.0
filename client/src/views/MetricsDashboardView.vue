<template>
  <div class="page">
    <div class="container" style="padding: 18px 0 34px">
      <div class="page-head">
        <h1>Results / Metrics : <span class="highlight">Dashboard</span></h1>
      </div>

      <div class="grid-3">
        <UiCard title="mAP" subtitle="AP@[0.50:0.95]">
          <div class="big">31.02%</div>
          <div class="text-muted">Iteration 3 (demo numbers)</div>
        </UiCard>
        <UiCard title="Recall" subtitle="AR by area size">
          <div class="big">88.6%</div>
          <div class="text-muted">High sensitivity, localization still improving</div>
        </UiCard>
        <UiCard title="AUC" subtitle="Per abnormality">
          <div class="big">0.82</div>
          <div class="text-muted">Illustrative dashboard view</div>
        </UiCard>
      </div>

      <div class="grid-2" style="margin-top: 16px">
        <UiCard title="Iteration comparison" subtitle="mAP over iterations">
          <ChartCanvas :config="iterationConfig" />
        </UiCard>

        <UiCard title="AUC by abnormality" subtitle="Bar chart">
          <ChartCanvas :config="aucConfig" />
        </UiCard>
      </div>

      <div class="grid-2" style="margin-top: 16px">
        <UiCard title="Precision/Recall" subtitle="Tradeoff (demo)">
          <ChartCanvas :config="prConfig" />
        </UiCard>

        <UiCard title="Notes" subtitle="How to read this">
          <ul class="list">
            <li>mAP summarizes detection quality across IoU thresholds.</li>
            <li>High recall can still coincide with weaker localization precision.</li>
            <li>Per-class AUC helps identify which abnormalities need more data/training.</li>
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
          labels: ["IT1", "IT2", "IT3"],
          datasets: [
            {
              label: "mAP",
              data: [0.22, 0.27, 0.3102],
              borderColor: "#2563eb",
              backgroundColor: "rgba(37,99,235,0.10)",
              tension: 0.35,
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

.highlight { color: var(--primary); }

.list { margin: 0; padding-left: 18px; color: var(--text-2); line-height: 1.7; }

.big { font-size: 34px; font-weight: 900; letter-spacing: -0.02em; color: var(--text); }
</style>

<style scoped>
.page { min-height: 100vh; background: var(--bg); }
.big { font-size: 34px; font-weight: 900; letter-spacing: -0.02em; color: var(--text); }
.list { margin: 0; padding-left: 18px; color: var(--text-2); line-height: 1.7; }
</style>

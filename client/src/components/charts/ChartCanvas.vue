<template>
  <div class="chart-wrap">
    <canvas ref="canvas" />
  </div>
</template>

<script>
import { Chart } from "chart.js/auto";

export default {
  name: "ChartCanvas",
  props: {
    config: { type: Object, required: true },
  },
  data() {
    return {
      chart: null,
    };
  },
  mounted() {
    this.renderChart();
  },
  beforeUnmount() {
    this.destroyChart();
  },
  watch: {
    config: {
      deep: true,
      handler() {
        this.renderChart();
      },
    },
  },
  methods: {
    destroyChart() {
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
    },
    renderChart() {
      this.destroyChart();
      const ctx = this.$refs.canvas?.getContext?.("2d");
      if (!ctx) return;
      this.chart = new Chart(ctx, this.config);
    },
  },
};
</script>

<style scoped>
.chart-wrap {
  position: relative;
  width: 100%;
}

canvas {
  width: 100% !important;
  height: 280px !important;
}
</style>

import { reactive } from "vue";

const state = reactive({
  toasts: [],
});

function addToast(toast) {
  const id = crypto?.randomUUID ? crypto.randomUUID() : String(Date.now() + Math.random());
  const timeoutMs = toast.timeoutMs ?? 3500;
  state.toasts.push({
    id,
    title: toast.title ?? "",
    message: toast.message ?? "",
    variant: toast.variant ?? "info", // info|success|warning|danger
  });

  if (timeoutMs > 0) {
    window.setTimeout(() => removeToast(id), timeoutMs);
  }

  return id;
}

function removeToast(id) {
  const index = state.toasts.findIndex((t) => t.id === id);
  if (index >= 0) state.toasts.splice(index, 1);
}

export function useToast() {
  return {
    toasts: state.toasts,
    addToast,
    removeToast,
  };
}

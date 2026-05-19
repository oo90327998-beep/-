import { createApp } from "vue";
import App from "./App.vue";

const app = createApp(App);

app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue Error]', err);
  console.error('[Vue Error Info]', info);
  console.error('[Vue Error Component]', instance);
};

window.addEventListener('unhandledrejection', (event) => {
  console.error('[Unhandled Promise]', event.reason);
});

app.mount("#app");


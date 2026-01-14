import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { viteSingleFile } from "vite-plugin-singlefile";
import { devDataPlugin } from "./gui/vite-plugin-dev-data";

export default defineConfig({
  plugins: [react(), tailwindcss(), devDataPlugin(), viteSingleFile()],
});

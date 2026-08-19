import { defineConfig } from "vite";

// やねうら王WASM(pthread/SharedArrayBuffer利用)を動かすには
// クロスオリジン分離(COOP/COEP)ヘッダーが必要。
const crossOriginIsolationHeaders = {
  "Cross-Origin-Opener-Policy": "same-origin",
  "Cross-Origin-Embedder-Policy": "require-corp",
};

export default defineConfig({
  // GitHub Pagesは https://<owner>.github.io/<repo>/ というサブパス配信になるため、
  // GITHUB_PAGES=true のビルド時のみベースパスをリポジトリ名にする。
  base: process.env.GITHUB_PAGES ? "/shogi/" : "/",
  server: { headers: crossOriginIsolationHeaders },
  preview: { headers: crossOriginIsolationHeaders },
});

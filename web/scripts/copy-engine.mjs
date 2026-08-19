// node_modules/yaneuraou.wasm から public/engine/ へ実行に必要なファイルをコピーする。
// (npm install 後に自動実行される。 public/engine の中身はサイズが大きいためGit管理しない)
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const src = join(root, "node_modules", "yaneuraou.wasm");
const dest = join(root, "public", "engine");

const files = [
  "yaneuraou.js",
  "yaneuraou.wasm",
  "yaneuraou.worker.js",
  "yaneuraou.data",
  "Copying.txt",
];

if (!existsSync(src)) {
  console.warn("yaneuraou.wasm がまだインストールされていません。npm install を実行してください。");
  process.exit(0);
}

mkdirSync(dest, { recursive: true });
for (const file of files) {
  copyFileSync(join(src, file), join(dest, file));
}
console.log(`エンジンファイルを ${dest} にコピーしました。`);

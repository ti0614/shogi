// やねうら王(WASM版)をUSIプロトコルで操作するためのWorkerラッパー。
// メインスレッドから postMessage されたUSIコマンド文字列をそのままエンジンに渡し、
// エンジンからの出力行をそのままメインスレッドへ postMessage で返す。
importScripts("yaneuraou.js");

// pthread(サブWorker)がスクリプトの場所を解決できるように明示しておく。
// (このWorker自身はdocumentを持たないため、指定しないとurlOrBlobがundefinedになり失敗する)
const moduleOverrides = {
  mainScriptUrlOrBlob: new URL("yaneuraou.js", self.location.href).href,
};

YaneuraOu(moduleOverrides).then((engine) => {
  engine.addMessageListener((line) => {
    postMessage(line);
  });
  onmessage = (e) => {
    engine.postMessage(e.data);
  };
  postMessage("__engine_ready__");
});

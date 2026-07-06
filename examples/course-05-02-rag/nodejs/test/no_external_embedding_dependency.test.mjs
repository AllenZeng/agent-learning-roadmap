import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const FILES_TO_CHECK = [
  "offline_pipeline.mjs",
  "online_pipeline.mjs",
  "retrieval_core.mjs",
  "package.json",
];

test("example does not depend on external embedding model packages", async () => {
  const packagePattern = new RegExp(
    [
      ["@hugging", "face"].join(""),
      ["trans", "formers"].join(""),
    ].join("/") +
      "|" +
      ["onnx", "runtime-web"].join("") +
      "|" +
      ["trans", "formers"].join("") +
      "\\.js",
    "i"
  );
  const optionPattern = new RegExp(
    ["EMBED", "DING_RETRIEVER"].join("") +
      "|" +
      ["--retriever emb", "edding"].join("") +
      "|" +
      ["--embedding", "-model"].join("")
  );

  for (const file of FILES_TO_CHECK) {
    const text = await readFile(new URL(`../${file}`, import.meta.url), "utf-8");
    assert.doesNotMatch(text, packagePattern, file);
    assert.doesNotMatch(text, optionPattern, file);
  }
});

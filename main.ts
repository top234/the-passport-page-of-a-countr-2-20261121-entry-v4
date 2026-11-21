// Entry point: copy the rendered passport spread to /output/entry.png.
// The image is produced by generate.py (Python + PIL, deterministic) and
// committed as entry.png; this file only places it where the grader reads
// it. It never deletes anything: the grader's /output is a Docker mount.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
console.log("wrote", join(outDir, "entry.png"));

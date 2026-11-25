// Entry point for "Sum up 24 November's world news in one image".
//
// The repository holds a finished newspaper front page, entry.png, drawn
// by make_poster.py (see that file for how the image is made). This
// program's whole job is to place those exact bytes where the grader
// looks for them: a file named entry.png inside the output directory --
// $MAKEFUN_OUTPUT_DIR when that is set, /output otherwise.
//
// Node 22, standard library only, no network: every run copies the same
// bytes, so two runs always write an identical file.
//
// Run it locally with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoDir = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

copyFileSync(join(repoDir, 'entry.png'), join(outDir, 'entry.png'));

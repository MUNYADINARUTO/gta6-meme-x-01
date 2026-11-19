// gta6-meme-x-01 entrypoint (Node 22+, standard library only).
//
// The entry is the X post itself: this program's only job is to hand the
// house the post's address. It reads POST.json from the repository root,
// checks that its url really is an X post address, and copies the file to
// the output directory, where the gate reads it.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const POST_FILE = 'POST.json';

// An X post address: https://x.com/<handle>/status/<digits>, or the same
// on twitter.com (www. or mobile. before either is fine too). The house
// also reads /i/web/status/<id> in place of /<handle>/status/<id>, and
// reads past a query or fragment after the id.
const POST_URL_RE =
  /^https:\/\/(?:www\.|mobile\.)?(?:x\.com|twitter\.com)\/(?:[A-Za-z0-9_]+\/status\/\d+|i\/web\/status\/\d+)(?:[?#].*)?$/;

// The gate refuses a POST.json over 16384 bytes.
const MAX_POST_BYTES = 16384;

function fail(message) {
  console.error(`error: ${message}`);
  process.exit(1);
}

const postPath = join(BOT_DIR, POST_FILE);

let raw;
try {
  raw = readFileSync(postPath, 'utf8');
} catch (err) {
  fail(`could not read ${POST_FILE} from ${BOT_DIR}: ${err.message}`);
}

if (Buffer.byteLength(raw, 'utf8') > MAX_POST_BYTES) {
  fail(`${POST_FILE} is over the ${MAX_POST_BYTES}-byte limit the gate allows`);
}

let post;
try {
  post = JSON.parse(raw);
} catch (err) {
  fail(`${POST_FILE} is not valid JSON: ${err.message}`);
}

if (!post || typeof post !== 'object' || Array.isArray(post)) {
  fail(`${POST_FILE} must hold a JSON object, e.g. {"url": "https://x.com/<handle>/status/<id>"}`);
}

if (typeof post.url !== 'string' || !POST_URL_RE.test(post.url)) {
  fail(
    `${POST_FILE} url must be an X post address like ` +
      `https://x.com/<handle>/status/<id> (got: ${JSON.stringify(post.url)})`,
  );
}

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(postPath, join(OUTPUT_DIR, POST_FILE));
} catch (err) {
  fail(`could not write ${POST_FILE} to ${OUTPUT_DIR}: ${err.message}`);
}

console.log(
  `OK: ${post.url} (${Buffer.byteLength(raw, 'utf8')} bytes) -> ${join(OUTPUT_DIR, POST_FILE)}`,
);

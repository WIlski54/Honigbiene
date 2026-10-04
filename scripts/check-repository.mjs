import { execFileSync } from 'node:child_process';
import { readFileSync, statSync } from 'node:fs';
import { extname } from 'node:path';

// Auch bereits versionierte, nachtraeglich ignorierte Dateien pruefen.
const files = [...new Set(execFileSync('git', [
  'ls-files', '--cached', '--others', '--exclude-standard', '-z',
], { encoding: 'utf8' }).split('\0').filter(Boolean))];
const errors = [];
const secretPatterns = [
  /\bAIzaSy[A-Za-z0-9_-]{33}\b/,
  /\bgh[pousr]_[A-Za-z0-9]{36,}\b/,
  /\bgithub_pat_[A-Za-z0-9_]{20,}\b/,
  /-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----/,
];
const textExtensions = new Set(['.js', '.mjs', '.cjs', '.py', '.json', '.html', '.md', '.txt', '.yml', '.yaml', '.example']);
let bytes = 0;
for (const file of files) {
  const name = file.split('/').at(-1);
  if ((/^\.env(?:\.|$)/.test(name) && name !== '.env.example') ||
      /\.(?:db(?:-wal|-shm)?|sqlite3?|key)$/i.test(name) ||
      /^(?:arbeitsblatt\/data|arbeitsblatt\/werkzeuge\/ausgabe)\//.test(file)) {
    errors.push(`${file}: Zugangsdaten oder Laufzeitdaten gehoeren nicht ins Repository.`);
  }
  const size = statSync(file).size;
  bytes += size;
  if (size > 100 * 1024 * 1024) errors.push(`${file}: groesser als das GitHub-Limit von 100 MiB.`);
  if (textExtensions.has(extname(file)) && secretPatterns.some(pattern => pattern.test(readFileSync(file, 'utf8')))) {
    errors.push(`${file}: moeglicher Zugangsschluessel. Inhalt wird nicht ausgegeben.`);
  }
}
if (errors.length) {
  for (const error of errors) console.error(error);
  process.exitCode = 1;
} else {
  console.log(`${files.length} Dateien, ${(bytes / 1024 / 1024).toFixed(1)} MiB: keine gesperrten Dateien oder bekannten Schluesselmuster.`);
  console.log('Die Musterpruefung ersetzt keine vollstaendige Sicherheitspruefung.');
}

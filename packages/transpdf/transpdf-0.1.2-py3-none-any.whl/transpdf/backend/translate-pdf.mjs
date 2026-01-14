// translate-pdf.mjs
//import processPDFModule from './translator.js'; // ← Default import
import { processPDF } from './translator.js';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Extract processPDF from the default export
//const { processPDF } = processPDFModule;

async function main() {
  const [inputPdf, outputDir, fromLang, toLang] = process.argv.slice(2);
  
  if (!inputPdf || !outputDir || !fromLang || !toLang) {
    console.error("Usage: node translate-pdf.mjs <input.pdf> <output_dir> <from_lang> <to_lang>");
    process.exit(1);
  }

  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

  const progressFile = path.join(outputDir, 'progress.txt');
  const progressCallback = (percent) => {
    fs.writeFileSync(progressFile, Math.round(percent).toString());
  };

  try {
    const outputPath = await processPDF(fromLang, toLang, inputPdf, outputDir, progressCallback);
    fs.writeFileSync(progressFile, "DONE:" + outputPath);
  } catch (err) {
    fs.writeFileSync(progressFile, "ERROR:" + err.message);
    throw err;
  }
}

main().catch(console.error);
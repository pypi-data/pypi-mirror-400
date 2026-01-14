// translator.js
import fs from 'fs-extra';
import path from 'path';
import { PDFDocument } from 'pdf-lib';
import tmp from 'tmp';
import { firefox } from 'playwright-extra';
import stealthPlugin from 'puppeteer-extra-plugin-stealth';
import sharp from 'sharp';

// Apply stealth to Firefox (this combo works)
const stealth = stealthPlugin();
firefox.use(stealth);

const { dirSync } = tmp;

// Function to convert PDF to images
const convertPDFToImages = async (pdfPath, outputDir, progressCallback) => {
  console.info('Converting PDF to images.. and save to', outputDir);
  fs.ensureDirSync(outputDir);
  const { pdf } = await import("pdf-to-img");
  try {
    const images = await pdf(pdfPath, { scale: 3 });
    let counter = 1;
    const imageArray = [];
    for await (const image of images) imageArray.push(image);

    for (let i = 0; i < imageArray.length; i++) {
      const jpegPath = `${outputDir}/page${(i + 1).toString().padStart(3, '0')}.jpeg`;
      await sharp(imageArray[i])
        .jpeg({ 
          quality: 100,
          progressive: false,
          chromaSubsampling: '4:4:4',
          trellisQuantisation: true,
          overshootDeringing: true,
          optimiseScans: true
        })
        .toFile(jpegPath);
      progressCallback((i + 1) / imageArray.length);
    }
    console.info('Pdf converted to images. 🌟');
  } catch (error) {
    console.error('Error converting PDF to images:', error);
  }
};

// Function to translate images — USE FRIEND'S EXACT LOGIC
const translateImage = async (inLang, outLang, browser, imagePath, outputDir) => {
  const baseName = path.basename(imagePath, path.extname(imagePath));
  const translatedImagePath = path.join(outputDir, `${baseName}_translated.jpeg`);

  try {
    const page = await browser.newPage();

    // ✅ FIXED URL: NO extra spaces
    await page.goto(`https://translate.google.com/?sl=${inLang}&tl=${outLang}&op=images`, {
      waitUntil: 'networkidle',
      timeout: 15000
    });

    // ✅ USE FRIEND'S EXACT SELECTOR (critical!)
    const fileInput = await page.locator('css=#yDmH0d > c-wiz > div > div.ToWKne > c-wiz > div.caTGn > c-wiz > div.iggndc > c-wiz > div > div > div > div.rlWbvd > div.gLXQIf > div.T12pLd > div:nth-child(1) > input');
    await fileInput.setInputFiles(imagePath);

    // ✅ Wait for exact translated image
    const translatedImage = await page.waitForSelector('div.CMhTbb:nth-child(2) > img:nth-child(1)', { timeout: 30000 });

    // ✅ Use friend's blob → base64 → sharp method (works for blob URLs)
    const blobUrl = await translatedImage.getAttribute('src');
    const base64Data = await page.evaluate((url) => {
      return new Promise((resolve, reject) => {
        fetch(url)
          .then(res => res.blob())
          .then(blob => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
          })
          .catch(reject);
      });
    }, blobUrl);

    const imageDataStr = base64Data.split(',')[1];
    const pngData = Buffer.from(imageDataStr, 'base64');
    await sharp(pngData)
      .jpeg({ 
        quality: 100,
        progressive: false,
        chromaSubsampling: '4:4:4',
        trellisQuantisation: true,
        overshootDeringing: true,
        optimiseScans: true
      })
      .toFile(translatedImagePath);

    await page.close();
    console.info(`${baseName} translated → ${translatedImagePath}`);
  } catch (error) {
    console.error(`Translation failed for ${imagePath}:`, error.message);
    await fs.copyFile(imagePath, translatedImagePath);
  }
};

// Combine images to PDF
const combineImagesToPDF = async (imagesDir, outputPdfPath) => {
  const pdfDoc = await PDFDocument.create();
  const imageFiles = fs.readdirSync(imagesDir)
    .filter(file => /\.(jpeg)$/i.test(file))
    .sort();

  for (const imageFile of imageFiles) {
    const imagePath = path.join(imagesDir, imageFile);
    const imageBytes = fs.readFileSync(imagePath);
    const image = await pdfDoc.embedJpg(imageBytes);
    const page = pdfDoc.addPage([image.width, image.height]);
    page.drawImage(image, { x: 0, y: 0, width: image.width, height: image.height });
  }

  fs.writeFileSync(outputPdfPath, await pdfDoc.save());
  console.log(`PDF successfully created at ${outputPdfPath}`);
};

// Main function
const processPDF = async (inLang, outLang, pdfPath, outputDir, progressCallback = () => {}) => {
  const tempDir1 = dirSync({ postfix: '_images' });
  const tempDir2 = dirSync({ postfix: '_translated_images' });
  fs.ensureDirSync(outputDir);
  const outputPdfPath = path.join(outputDir, path.basename(pdfPath, path.extname(pdfPath)) + '_translated.pdf');

  // ✅ Use FIREFOX + STEALTH (this is what works)
  const browser = await firefox.launch({ 
    headless: true, 
    ignoreHTTPSErrors: true 
  });

  try {
    await convertPDFToImages(pdfPath, tempDir1.name, (progress) => progressCallback(Math.round(10 * progress)));

    const imageFiles = fs.readdirSync(tempDir1.name)
      .filter(file => /\.(jpeg)$/i.test(file))
      .sort();
    const total = imageFiles.length;

    for (let i = 0; i < total; i++) {
      const imagePath = path.join(tempDir1.name, imageFiles[i]);
      await translateImage(inLang, outLang, browser, imagePath, tempDir2.name);
      const progress = 10 + Math.round((80 * (i + 1)) / total);
      progressCallback(progress);
    }

    await combineImagesToPDF(tempDir2.name, outputPdfPath);
    progressCallback(100);
    console.info('All done! 🎉');
  } catch (error) {
    console.error('Error processing PDF:', error);
  } finally {
    fs.removeSync(tempDir1.name);
    fs.removeSync(tempDir2.name);
    await browser.close();
  }

  return outputPdfPath;
};

export { processPDF };
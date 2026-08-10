const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const html = 'file://' + path.resolve('build/flyer.html');
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox', '--force-color-profile=srgb', '--font-render-hinting=none']
  });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 2 });
  await page.goto(html, { waitUntil: 'networkidle' });
  await page.evaluate(async () => { await document.fonts.ready; });
  await page.waitForTimeout(500);
  const el = await page.$('#flyer');
  await el.screenshot({ path: 'build/flyer.png' });
  await browser.close();
  console.log('rendered build/flyer.png');
})();

const { chromium } = require('playwright');
const path = require('path');
const sizes = [
  { name: '4x6',   w: 800, h: 1200, scale: 3 },   // 2400x3600 = 400dpi
  { name: '5x7',   w: 800, h: 1120, scale: 3 },   // 2400x3360 = 480dpi
  { name: '85x11', w: 850, h: 1100, scale: 3 },   // 2550x3300 = 300dpi
];
(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox', '--force-color-profile=srgb', '--font-render-hinting=none']
  });
  for (const s of sizes) {
    const html = 'file://' + path.resolve(`build/agenda_${s.name}.html`);
    const page = await browser.newPage({ viewport: { width: s.w, height: s.h }, deviceScaleFactor: s.scale });
    await page.goto(html, { waitUntil: 'networkidle' });
    await page.evaluate(async () => { await document.fonts.ready; });
    await page.waitForTimeout(400);
    const el = await page.$('#page');
    await el.screenshot({ path: `build/agenda_${s.name}.png` });
    await page.close();
    console.log(`rendered build/agenda_${s.name}.png (${s.w*s.scale}x${s.h*s.scale})`);
  }
  await browser.close();
})();

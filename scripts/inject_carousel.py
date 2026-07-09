#!/usr/bin/env python3
"""One-off script: inject the photo carousel (CSS/markup/JS) into berghain-tracker.html."""
import json

HTML_PATH = "berghain-tracker.html"
DATA_PATH = "/tmp/carousel_data.json"

with open(DATA_PATH) as f:
    carousel = json.load(f)

with open(HTML_PATH) as f:
    html = f.read()

carousel_js_array = json.dumps(carousel)

CSS_BLOCK = """
  .carousel { position: relative; width: 100%; height: clamp(220px, 38vw, 420px); overflow: hidden; background: var(--bg); }
  .carousel-slide {
    position: absolute; inset: 0; background-size: cover; background-position: center;
    opacity: 0; transition: opacity 900ms ease;
    filter: grayscale(0.25) contrast(1.05) brightness(0.8);
  }
  .carousel-slide.active { opacity: 1; }
  .carousel-overlay {
    position: absolute; inset: 0; pointer-events: none;
    background: linear-gradient(to bottom, rgba(22,21,26,0) 45%, var(--bg) 100%);
  }
  .carousel-caption {
    position: absolute; left: var(--space-4); bottom: var(--space-4); color: var(--fg);
    font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; max-width: 70%;
  }
  .carousel-caption .credit { color: var(--muted); font-size: 10px; display: block; margin-top: 2px; letter-spacing: 0.03em; }
  .carousel-nav {
    position: absolute; top: 50%; transform: translateY(-50%);
    background: rgba(22,21,26,0.55); color: var(--fg); border: 1px solid var(--rule);
    width: 36px; height: 36px; cursor: pointer; font-family: var(--font); font-size: 18px; line-height: 1;
  }
  .carousel-nav:hover { border-color: var(--fg); }
  .carousel-nav.prev { left: var(--space-3); }
  .carousel-nav.next { right: var(--space-3); }
  .carousel-dots { position: absolute; right: var(--space-4); bottom: var(--space-4); display: flex; gap: 6px; }
  .carousel-dots .dot { width: 8px; height: 8px; background: var(--rule); cursor: pointer; border: none; padding: 0; }
  .carousel-dots .dot.active { background: var(--panorama); }
  @media (prefers-reduced-motion: reduce) {
    .carousel-slide { transition: none; }
  }
"""

MARKUP_BLOCK = """
<div class="carousel" id="carousel">
  <div class="carousel-track" id="carousel-track"></div>
  <button class="carousel-nav prev" id="carousel-prev" aria-label="Previous photo">&#8249;</button>
  <button class="carousel-nav next" id="carousel-next" aria-label="Next photo">&#8250;</button>
  <div class="carousel-caption">
    <span id="carousel-caption-text"></span>
    <span class="credit" id="carousel-caption-credit"></span>
  </div>
  <div class="carousel-dots" id="carousel-dots"></div>
</div>
"""

JS_BLOCK = f"""
const CAROUSEL = {carousel_js_array};
let carouselIndex = 0;
let carouselTimer = null;

function renderCarousel() {{
  const track = document.getElementById('carousel-track');
  const dotsEl = document.getElementById('carousel-dots');
  track.innerHTML = CAROUSEL.map((c, i) =>
    `<div class="carousel-slide${{i === carouselIndex ? ' active' : ''}}" style="background-image:url('${{c.src}}')"></div>`
  ).join('') + '<div class="carousel-overlay"></div>';
  dotsEl.innerHTML = CAROUSEL.map((c, i) =>
    `<button class="dot${{i === carouselIndex ? ' active' : ''}}" data-i="${{i}}" aria-label="Show photo ${{i + 1}} of ${{CAROUSEL.length}}"></button>`
  ).join('');
  document.getElementById('carousel-caption-text').textContent = CAROUSEL[carouselIndex].caption;
  document.getElementById('carousel-caption-credit').textContent = CAROUSEL[carouselIndex].credit;
}}

function goToSlide(i) {{
  carouselIndex = (i + CAROUSEL.length) % CAROUSEL.length;
  renderCarousel();
}}

function resetAutoplay() {{
  if (carouselTimer) clearInterval(carouselTimer);
  startCarouselAutoplay();
}}

function startCarouselAutoplay() {{
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  carouselTimer = setInterval(() => goToSlide(carouselIndex + 1), 5000);
}}

document.getElementById('carousel-prev').addEventListener('click', () => {{ goToSlide(carouselIndex - 1); resetAutoplay(); }});
document.getElementById('carousel-next').addEventListener('click', () => {{ goToSlide(carouselIndex + 1); resetAutoplay(); }});
document.getElementById('carousel-dots').addEventListener('click', (e) => {{
  const dot = e.target.closest('.dot');
  if (dot) {{ goToSlide(Number(dot.dataset.i)); resetAutoplay(); }}
}});

renderCarousel();
startCarouselAutoplay();
"""

assert "</style>" in html
html = html.replace("</style>", CSS_BLOCK + "</style>", 1)

assert '<div class="page">' in html
html = html.replace('<div class="page">', MARKUP_BLOCK + '\n<div class="page">', 1)

assert "setDay('friday');\n</script>" in html
html = html.replace("setDay('friday');\n</script>", "setDay('friday');\n" + JS_BLOCK + "</script>", 1)

with open(HTML_PATH, "w") as f:
    f.write(html)

print("Injected carousel. New file size:", len(html), "chars")

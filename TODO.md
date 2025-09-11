# Website Optimization Plan for Apartaments Alanya

## Information Gathered
- **Site Structure**: Multi-language website (EN, UA, TR, CZ, RU) for apartment rentals in Alanya
- **Tech Stack**: Flask app serving static HTML/CSS/JS, SQLite database for prices, multiple image sliders
- **Main Issues Identified**:
  - 50+ images (apartments, icons, video background) causing slow loading
  - Large video file (headerBG.mp4) as background
  - No image optimization or lazy loading
  - Multiple HTTP requests for assets
  - Heavy animations and transitions
  - Google Maps iframes loading on page load
  - Unminified CSS/JS files
  - No caching headers

## Plan
### 1. Image Optimization
- [ ] Compress all images in `/img/` folder using tools like TinyPNG or ImageOptim
- [ ] Convert images to WebP format with fallbacks
- [ ] Resize large images to appropriate dimensions
- [ ] Optimize video background (compress or replace with static image)

### 2. Loading Performance
- [ ] Implement lazy loading for apartment slider images
- [ ] Add preload hints for critical resources (fonts, CSS)
- [ ] Defer non-critical JavaScript
- [ ] Optimize Google Fonts loading (preload, subset)

### 3. Code Optimization
- [ ] Minify CSS files (style.css, animations.css)
- [ ] Minify JavaScript (script.js)
- [ ] Remove unused CSS/JS code
- [ ] Optimize animations (reduce complexity, use will-change property)

### 4. Asset Management
- [ ] Combine multiple CSS files into one
- [ ] Combine multiple JS files into one
- [ ] Use CDN for static assets (images, fonts)
- [ ] Add proper cache headers in Flask app

### 5. Slider Optimization
- [ ] Load slider images on demand instead of all at once
- [ ] Implement progressive image loading
- [ ] Add loading placeholders for images

### 6. Map Optimization
- [ ] Lazy load Google Maps iframes
- [ ] Use static map images as placeholders
- [ ] Optimize map embed settings

### 7. Flask App Optimization
- [ ] Add gzip compression
- [ ] Implement proper caching headers
- [ ] Optimize database queries
- [ ] Add asset versioning for cache busting

## Dependent Files to Edit
- `index.html` (and other language versions)
- `style.css`
- `animations.css`
- `script.js`
- `app.py`
- All images in `/img/` folder

## Followup Steps
- [ ] Test loading speed using tools like Google PageSpeed Insights
- [ ] Test on different devices and network conditions
- [ ] Monitor Core Web Vitals
- [ ] Implement monitoring for performance metrics

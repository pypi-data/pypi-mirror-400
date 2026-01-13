Deployment

This is a static site. Recommended: GitHub Pages or Netlify.

GitHub Pages (root):
1. Commit the 'realestate-site' folder to your repo root.
2. In GitHub repo settings -> Pages, set source to main branch / root or /docs if you place files there.
3. Visit your-site.github.io

Netlify:
1. Drag & drop the folder or connect repo.
2. Ensure publish directory is root of project.

Notes:
- Add caching headers via platform settings.
- For production, pre-generate optimized images and replace assets/img files with webp + sizes.
- Minify css/styles.css and js/*.js using online minifier or build script.
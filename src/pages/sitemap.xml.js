import data from '../data/site-data.json';

export async function GET() {
  const urls = [
    '/',
    '/page/2/',
    ...data.categories.map((c) => `/category/${c.slug}/`),
    ...data.posts.map((p) => p.path),
    ...data.pages.filter((p) => p.path !== '/').map((p) => p.path),
  ];
  const unique = [...new Set(urls)].filter(Boolean);
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${unique
    .map((path) => `  <url><loc>https://visitbulharsko.cz${path}</loc></url>`)
    .join('\n')}\n</urlset>`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}

import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

const site = process.env.SITE_URL || 'https://visitbulharsko.cz';
const rawBase = process.env.BASE_PATH || '/';
const base = !rawBase || rawBase === '/' || /^[A-Za-z]:\//.test(rawBase)
  ? '/'
  : `/${rawBase.replace(/^\/+|\/+$/g, '')}`;

export default defineConfig({
  site,
  base,
  integrations: [tailwind()],
  output: 'static',
  trailingSlash: 'always',
});

function normalizeBase(base = '/') {
  // Git Bash/MSYS can path-convert BASE_PATH=/ into C:/Program Files/Git/ during Windows builds.
  // Treat accidental Windows drive paths as the site root so launch builds do not emit broken URLs.
  if (!base || base === '/' || /^[A-Za-z]:\//.test(base)) return '';
  return base.startsWith('/') ? base.replace(/\/$/, '') : `/${base.replace(/^\/+|\/$/g, '')}`;
}

function normalizePath(path = '/') {
  if (!path || path === '/' || /^[A-Za-z]:\//.test(path)) return '/';
  return path.startsWith('/') ? path : `/${path}`;
}

export function withBase(path = '/') {
  if (!path) return path;
  if (/^(https?:)?\/\//.test(path) || path.startsWith('mailto:') || path.startsWith('tel:') || path.startsWith('#')) {
    return path;
  }
  const cleanBase = normalizeBase(import.meta.env.BASE_URL || '/');
  const cleanPath = normalizePath(path);
  return `${cleanBase}${cleanPath}` || '/';
}

export function canonicalUrl(path = '/') {
  const site = (import.meta.env.SITE || 'https://visitbulharsko.cz').replace(/\/$/, '');
  const cleanBase = normalizeBase(import.meta.env.BASE_URL || '/');
  const cleanPath = normalizePath(path);
  return `${site}${cleanBase}${cleanPath}`;
}

export function absoluteUrl(path = '/') {
  if (!path) return path;
  if (/^https?:\/\//.test(path)) return path;
  return canonicalUrl(withBase(path));
}

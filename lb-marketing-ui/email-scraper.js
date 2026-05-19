import https from 'node:https';
import http from 'node:http';

const BLOCKED_HOSTS = new Set([
  'yelp.com', 'www.yelp.com', 'facebook.com', 'www.facebook.com',
  'instagram.com', 'www.instagram.com', 'google.com', 'www.google.com',
  'maps.google.com', 'linkedin.com', 'www.linkedin.com', 'twitter.com',
  'x.com', 'tiktok.com', 'youtube.com', 'youtu.be',
]);

const BLOCKED_EMAIL_DOMAINS = new Set([
  'example.com', 'sentry.io', 'wixpress.com', 'users.noreply.github.com',
  'email.com', 'domain.com', 'yelp.com', 'google.com', 'facebook.com',
]);

const PREFERRED_LOCALS = ['info', 'contact', 'hello', 'office', 'sales', 'support', 'admin'];

const EMAIL_REGEX = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;

const domainLastFetch = new Map();
const DOMAIN_COOLDOWN_MS = 500;
const REQUEST_TIMEOUT_MS = 8000;
const MAX_BODY_CHARS = 500_000;
const MAX_REDIRECTS = 3;
const MAX_EXTRA_PAGES = 2;

const USER_AGENT = 'Mozilla/5.0 (compatible; LBMarketingProspector/1.0; +https://lbmarketing.com)';

function jsonResponse(res, statusCode, body) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  });
  res.end(JSON.stringify(body));
}

function isBlockedHost(hostname) {
  const h = hostname.toLowerCase().replace(/^www\./, '');
  for (const blocked of BLOCKED_HOSTS) {
    if (h === blocked || h.endsWith('.' + blocked)) return true;
  }
  return false;
}

function isScrapableUrl(urlStr) {
  try {
    const u = new URL(urlStr);
    if (!['http:', 'https:'].includes(u.protocol)) return false;
    return !isBlockedHost(u.hostname);
  } catch {
    return false;
  }
}

function normalizeUrl(urlStr) {
  const trimmed = String(urlStr).trim();
  const withProto = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
  return new URL(withProto).href;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitForDomain(hostname) {
  const key = hostname.toLowerCase();
  const last = domainLastFetch.get(key) || 0;
  const elapsed = Date.now() - last;
  if (elapsed < DOMAIN_COOLDOWN_MS) {
    await sleep(DOMAIN_COOLDOWN_MS - elapsed);
  }
  domainLastFetch.set(key, Date.now());
}

function fetchUrl(urlStr, redirectCount = 0) {
  return new Promise((resolve, reject) => {
    let parsed;
    try {
      parsed = new URL(urlStr);
    } catch (e) {
      reject(e);
      return;
    }

    const lib = parsed.protocol === 'https:' ? https : http;
    let settled = false;

    const finish = (fn, value) => {
      if (settled) return;
      settled = true;
      fn(value);
    };

    const req = lib.get(
      urlStr,
      {
        headers: { 'User-Agent': USER_AGENT, Accept: 'text/html,application/xhtml+xml' },
      },
      (res) => {
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location && redirectCount < MAX_REDIRECTS) {
          let next;
          try {
            next = new URL(res.headers.location, urlStr).href;
          } catch (e) {
            res.resume();
            finish(reject, e);
            return;
          }
          res.resume();
          fetchUrl(next, redirectCount + 1).then(
            (body) => finish(resolve, body),
            (err) => finish(reject, err),
          );
          return;
        }

        if (res.statusCode !== 200) {
          res.resume();
          finish(reject, new Error(`HTTP ${res.statusCode}`));
          return;
        }

        let body = '';
        res.setEncoding('utf8');
        res.on('data', (chunk) => {
          body += chunk;
          if (body.length > MAX_BODY_CHARS) {
            req.destroy();
            finish(resolve, body.slice(0, MAX_BODY_CHARS));
          }
        });
        res.on('end', () => finish(resolve, body));
        res.on('error', (err) => finish(reject, err));
      },
    );

    req.on('error', (err) => finish(reject, err));
    req.setTimeout(REQUEST_TIMEOUT_MS, () => {
      req.destroy();
      finish(reject, new Error('timeout'));
    });
  });
}

function extractEmailsFromHtml(html) {
  const found = new Set();

  const mailtoRe = /mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/gi;
  let m;
  while ((m = mailtoRe.exec(html)) !== null) {
    found.add(m[1].toLowerCase());
  }

  const matches = html.match(EMAIL_REGEX) || [];
  for (const raw of matches) {
    const email = raw.toLowerCase().replace(/[.,;]+$/, '');
    if (isValidEmail(email)) found.add(email);
  }

  return [...found];
}

function isValidEmail(email) {
  if (!email || email.length > 80) return false;
  if (email.includes('..') || email.startsWith('.') || email.endsWith('.')) return false;
  const parts = email.split('@');
  if (parts.length !== 2) return false;
  const [local, domain] = parts;
  if (!local || !domain || !domain.includes('.')) return false;
  if (BLOCKED_EMAIL_DOMAINS.has(domain)) return false;
  if (/\.(png|jpg|jpeg|gif|svg|webp|css|js)$/i.test(domain)) return false;
  if (local.includes('noreply') || local.includes('no-reply')) return false;
  if (local.length < 2) return false;
  return true;
}

function rankEmails(emails) {
  return [...emails].sort((a, b) => scoreEmail(b) - scoreEmail(a));
}

function scoreEmail(email) {
  const [local, domain] = email.split('@');
  let score = 0;
  if (PREFERRED_LOCALS.some(p => local === p || local.startsWith(p + '.'))) score += 10;
  if (local.includes('contact')) score += 5;
  if (local.includes('info')) score += 5;
  if (domain.includes('wix') || domain.includes('squarespace')) score -= 3;
  return score;
}

async function scrapePage(urlStr) {
  const html = await fetchUrl(urlStr);
  return extractEmailsFromHtml(html);
}

const SCRAPE_DEADLINE_MS = 22000;

function withDeadline(promise, ms, label = 'scrape') {
  return Promise.race([
    promise,
    sleep(ms).then(() => {
      throw new Error(`${label} timed out after ${ms}ms`);
    }),
  ]);
}

export async function scrapeEmailFromWebsite(urlStr) {
  if (!urlStr || !isScrapableUrl(urlStr)) {
    return { email: null, candidates: [], source: 'website_scrape', error: 'not_scrapable' };
  }

  try {
    return await withDeadline(scrapeEmailFromWebsiteInner(urlStr), SCRAPE_DEADLINE_MS);
  } catch (err) {
    return {
      email: null,
      candidates: [],
      source: 'website_scrape',
      error: err.message || 'scrape_failed',
    };
  }
}

async function scrapeEmailFromWebsiteInner(urlStr) {
  const startUrl = normalizeUrl(urlStr);
  const hostname = new URL(startUrl).hostname;

  try {
    await waitForDomain(hostname);

    const allEmails = new Set();
    const homepageEmails = await scrapePage(startUrl);
    homepageEmails.forEach(e => allEmails.add(e));

    if (allEmails.size > 0) {
      const ranked = rankEmails([...allEmails]);
      return {
        email: ranked[0],
        candidates: ranked,
        source: 'website_scrape',
        error: null,
      };
    }

    const extraPaths = ['/contact', '/contact-us', '/about'];
    const origin = new URL(startUrl).origin;
    let extraFetched = 0;
    for (const path of extraPaths) {
      if (extraFetched >= MAX_EXTRA_PAGES) break;
      const pageUrl = origin + path;
      try {
        await waitForDomain(hostname);
        const more = await withDeadline(scrapePage(pageUrl), REQUEST_TIMEOUT_MS + 1000, 'page');
        if (more.length > 0) {
          more.forEach(e => allEmails.add(e));
          extraFetched++;
          break;
        }
      } catch {
        // optional paths may 404 or timeout
      }
    }

    const ranked = rankEmails([...allEmails]);
    const email = ranked[0] || null;

    return {
      email,
      candidates: ranked,
      source: 'website_scrape',
      error: email ? null : 'no_email_found',
    };
  } catch (err) {
    return {
      email: null,
      candidates: [],
      source: 'website_scrape',
      error: err.message || 'scrape_failed',
    };
  }
}

export function handleScrapeEmailRequest(query, res) {
  const url = query.url;
  if (!url) {
    return jsonResponse(res, 400, { error: 'Missing url parameter' });
  }

  scrapeEmailFromWebsite(url)
    .then(result => jsonResponse(res, 200, result))
    .catch(err => jsonResponse(res, 500, { error: err.message }));
}

export { isScrapableUrl };

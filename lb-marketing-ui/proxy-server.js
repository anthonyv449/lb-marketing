import http from 'node:http';
import https from 'node:https';
import { handleScrapeEmailRequest } from './email-scraper.js';

const PORT = 3001;
const PROXY_TIMEOUT_MS = 30000;

function queryFromSearchParams(searchParams) {
  const query = {};
  for (const [key, value] of searchParams.entries()) {
    query[key] = value;
  }
  return query;
}

function proxyRequest(targetUrl, headers, res) {
  const parsed = new URL(targetUrl);
  const options = {
    hostname: parsed.hostname,
    port: parsed.port || 443,
    path: parsed.pathname + parsed.search,
    method: 'GET',
    headers: { ...headers, host: parsed.hostname },
  };

  const proxyReq = https.request(options, (proxyRes) => {
    let body = '';
    proxyRes.on('data', chunk => { body += chunk; });
    proxyRes.on('end', () => {
      res.writeHead(proxyRes.statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
      });
      res.end(body);
    });
  });

  proxyReq.on('error', (err) => {
    res.writeHead(502, {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    });
    res.end(JSON.stringify({ error: `Proxy error: ${err.message}` }));
  });

  proxyReq.setTimeout(PROXY_TIMEOUT_MS, () => {
    proxyReq.destroy();
    if (!res.headersSent) {
      res.writeHead(504, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      });
      res.end(JSON.stringify({ error: 'Upstream request timed out' }));
    }
  });

  proxyReq.end();
}

const server = http.createServer((req, res) => {
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': '*',
    });
    return res.end();
  }

  let requestUrl;
  try {
    requestUrl = new URL(req.url || '/', `http://127.0.0.1:${PORT}`);
  } catch {
    res.writeHead(400, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
    return res.end(JSON.stringify({ error: 'Invalid request URL' }));
  }

  const pathname = requestUrl.pathname;
  const query = queryFromSearchParams(requestUrl.searchParams);

  if (pathname === '/health-check-ping') {
    res.writeHead(200, {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    });
    return res.end(JSON.stringify({ status: 'ok' }));
  }

  if (pathname === '/google/textsearch') {
    const { query: q, key } = query;
    if (!q || !key) {
      res.writeHead(400, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
      return res.end(JSON.stringify({ error: 'Missing query or key parameter' }));
    }
    const target = `https://maps.googleapis.com/maps/api/place/textsearch/json?query=${encodeURIComponent(q)}&key=${key}`;
    return proxyRequest(target, {}, res);
  }

  if (pathname === '/google/details') {
    const { place_id, key } = query;
    if (!place_id || !key) {
      res.writeHead(400, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
      return res.end(JSON.stringify({ error: 'Missing place_id or key parameter' }));
    }
    const target = `https://maps.googleapis.com/maps/api/place/details/json?place_id=${encodeURIComponent(place_id)}&fields=website,formatted_phone_number&key=${key}`;
    return proxyRequest(target, {}, res);
  }

  if (pathname === '/yelp/search') {
    const { term, location, key } = query;
    if (!term || !location || !key) {
      res.writeHead(400, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
      return res.end(JSON.stringify({ error: 'Missing term, location, or key parameter' }));
    }
    const target = `https://api.yelp.com/v3/businesses/search?term=${encodeURIComponent(term)}&location=${encodeURIComponent(location)}&limit=20`;
    return proxyRequest(target, { Authorization: `Bearer ${key}` }, res);
  }

  if (pathname === '/yelp/business') {
    const { id, key } = query;
    if (!id || !key) {
      res.writeHead(400, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
      return res.end(JSON.stringify({ error: 'Missing id or key parameter' }));
    }
    const target = `https://api.yelp.com/v3/businesses/${encodeURIComponent(id)}`;
    return proxyRequest(target, { Authorization: `Bearer ${key}` }, res);
  }

  if (pathname === '/scrape/email') {
    return handleScrapeEmailRequest(query, res);
  }

  res.writeHead(404, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
  res.end(JSON.stringify({ error: 'Unknown route' }));
});

server.listen(PORT, () => {
  console.log(`Proxy server running at http://localhost:${PORT}`);
  console.log('Routes:');
  console.log('  GET /google/textsearch?query=...&key=...');
  console.log('  GET /google/details?place_id=...&key=...');
  console.log('  GET /yelp/search?term=...&location=...&key=...');
  console.log('  GET /yelp/business?id=...&key=...');
  console.log('  GET /scrape/email?url=...');
});

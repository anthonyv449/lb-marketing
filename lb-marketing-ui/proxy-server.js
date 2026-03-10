import http from 'node:http';
import https from 'node:https';
import { parse as parseUrl } from 'node:url';

const PORT = 3001;

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

  const parsed = parseUrl(req.url, true);

  if (parsed.pathname === '/health-check-ping') {
    res.writeHead(200, {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    });
    return res.end(JSON.stringify({ status: 'ok' }));
  }

  if (parsed.pathname === '/google/textsearch') {
    const { query, key } = parsed.query;
    if (!query || !key) {
      res.writeHead(400, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
      return res.end(JSON.stringify({ error: 'Missing query or key parameter' }));
    }
    const target = `https://maps.googleapis.com/maps/api/place/textsearch/json?query=${encodeURIComponent(query)}&key=${key}`;
    return proxyRequest(target, {}, res);
  }

  if (parsed.pathname === '/google/details') {
    const { place_id, key } = parsed.query;
    if (!place_id || !key) {
      res.writeHead(400, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
      return res.end(JSON.stringify({ error: 'Missing place_id or key parameter' }));
    }
    const target = `https://maps.googleapis.com/maps/api/place/details/json?place_id=${encodeURIComponent(place_id)}&fields=website,formatted_phone_number&key=${key}`;
    return proxyRequest(target, {}, res);
  }

  if (parsed.pathname === '/yelp/search') {
    const { term, location, key } = parsed.query;
    if (!term || !location || !key) {
      res.writeHead(400, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
      return res.end(JSON.stringify({ error: 'Missing term, location, or key parameter' }));
    }
    const target = `https://api.yelp.com/v3/businesses/search?term=${encodeURIComponent(term)}&location=${encodeURIComponent(location)}&limit=20`;
    return proxyRequest(target, { 'Authorization': `Bearer ${key}` }, res);
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
});

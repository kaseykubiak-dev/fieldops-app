/**
 * meraki-proxy.js  (Catalyst Center edition)
 * Local CORS proxy for the Cisco Catalyst Center API.
 * Handles token auth automatically — fetches a session token on
 * startup, caches it for ~5.5 hrs, and re-auths on 401.
 *
 * Usage:  node meraki-proxy.js
 * Runs on http://localhost:3001
 */

const http  = require('http');
const https = require('https');

const CATALYST = {
  host:     'sandboxdnac.cisco.com',
  username: 'devnetuser',
  password: 'Cisco123!'
};

const PORT = process.env.PORT || 3001;

let cachedToken  = null;
let tokenExpires = 0;

// ── Token auth ────────────────────────────────────────────────────────────────
function fetchToken() {
  return new Promise((resolve, reject) => {
    const creds = Buffer.from(`${CATALYST.username}:${CATALYST.password}`).toString('base64');
    const req = https.request({
      hostname:           CATALYST.host,
      path:               '/dna/system/api/v1/auth/token',
      method:             'POST',
      rejectUnauthorized: false,
      headers: {
        'Authorization': `Basic ${creds}`,
        'Content-Type':  'application/json',
        'Content-Length': '0'
      }
    }, (res) => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => {
        try {
          const json = JSON.parse(raw);
          if (!json.Token) return reject(new Error(`Auth failed (${res.statusCode}): ${raw}`));
          resolve(json.Token);
        } catch (e) { reject(new Error('Invalid auth response')); }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function getToken() {
  if (cachedToken && Date.now() < tokenExpires) return cachedToken;
  console.log('Fetching new Catalyst Center token…');
  cachedToken  = await fetchToken();
  tokenExpires = Date.now() + (5.5 * 60 * 60 * 1000); // 5.5 hours
  console.log('Token acquired ✓');
  return cachedToken;
}

// ── Proxy a single request ────────────────────────────────────────────────────
function catalystGet(path, token) {
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname:           CATALYST.host,
      path:               `/dna/intent/api/v1${path}`,
      method:             'GET',
      rejectUnauthorized: false,
      headers: {
        'X-Auth-Token': token,
        'Accept':       'application/json'
      }
    }, (res) => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => resolve({ status: res.statusCode, body: raw }));
    });
    req.on('error', reject);
    req.end();
  });
}

// ── HTTP server ───────────────────────────────────────────────────────────────
http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin',  '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept');

  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }
  if (req.method !== 'GET')     { res.writeHead(405); res.end(JSON.stringify({ error: 'Method not allowed' })); return; }

  console.log(`→ ${req.url}`);

  try {
    let token  = await getToken();
    let result = await catalystGet(req.url, token);

    // Token expired mid-session — refresh once and retry
    if (result.status === 401) {
      cachedToken = null;
      token  = await getToken();
      result = await catalystGet(req.url, token);
    }

    res.writeHead(result.status, { 'Content-Type': 'application/json' });
    res.end(result.body);

  } catch (err) {
    console.error('Proxy error:', err.message);
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: err.message }));
  }

}).listen(PORT, async () => {
  console.log(`Catalyst Center proxy ready → http://localhost:${PORT}`);
  console.log(`Host: ${CATALYST.host}\n`);
  try { await getToken(); } catch (e) { console.error('Startup token error:', e.message); }
});

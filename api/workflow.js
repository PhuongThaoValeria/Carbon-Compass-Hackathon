export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
    return res.status(204).end();
  }
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'method_not_allowed' });
  }

  const difyBase = process.env.DIFY_BASE || 'https://api.dify.ai';
  const difyKey = process.env.DIFY_API_KEY;
  if (!difyKey) {
    return res.status(500).json({ error: 'missing DIFY_API_KEY' });
  }

  let payload;
  try {
    const text = await streamToString(req);
    payload = JSON.parse(text);
  } catch {
    return res.status(400).json({ error: 'invalid_json' });
  }

  const sourceUrl = payload?.source_url || payload?.inputfile;
  const user = payload?.user || 'demo-user';
  if (!sourceUrl) {
    return res.status(400).json({ error: 'missing source_url' });
  }

  const body = {
    inputs: { inputfile: sourceUrl },
    response_mode: 'blocking',
    user,
  };

  const r = await fetch(`${difyBase}/v1/workflows/run`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${difyKey}`,
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
      Accept: '*/*',
      Origin: req.headers.origin || `https://${req.headers.host}`,
    },
    body: JSON.stringify(body),
  });
  const text = await r.text();
  let json;
  try { json = JSON.parse(text); } catch { json = { raw: text }; }
  if (!r.ok) return res.status(502).json({ error: 'workflow_failed', detail: json });
  return res.status(200).json(json);
}

function streamToString(stream) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    stream.on('data', (chunk) => chunks.push(Buffer.from(chunk)));
    stream.on('error', (err) => reject(err));
    stream.on('end', () => resolve(Buffer.concat(chunks).toString('utf-8')));
  });
}
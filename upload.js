import busboy from 'busboy';

export const config = { api: { bodyParser: false } };

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

  try {
    const { filename, mimetype, buffer } = await parseFile(req);

    const blob = new Blob([buffer], { type: mimetype || 'application/octet-stream' });
    const form = new FormData();
    form.append('file', blob, filename || 'upload.bin');

    const r = await fetch(`${difyBase}/v1/files/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${difyKey}`,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        Accept: '*/*',
        Origin: req.headers.origin || `https://${req.headers.host}`,
      },
      body: form,
    });
    const text = await r.text();
    let json;
    try { json = JSON.parse(text); } catch { json = { raw: text }; }
    if (!r.ok) return res.status(502).json({ error: 'upload_failed', detail: json });
    return res.status(200).json(json);
  } catch (err) {
    return res.status(400).json({ error: 'parse_failed', detail: String(err) });
  }
}

function parseFile(req) {
  return new Promise((resolve, reject) => {
    const bb = busboy({ headers: req.headers });
    let fileBuffer = Buffer.alloc(0);
    let filename = '';
    let mimetype = '';

    bb.on('file', (_name, file, info) => {
      filename = info?.filename || 'upload.bin';
      mimetype = info?.mimeType || info?.mime || 'application/octet-stream';
      file.on('data', (data) => { fileBuffer = Buffer.concat([fileBuffer, data]); });
    });
    bb.on('error', reject);
    bb.on('finish', () => {
      if (!fileBuffer || fileBuffer.length === 0) return reject(new Error('missing file field "file"'));
      resolve({ filename, mimetype, buffer: fileBuffer });
    });
    req.pipe(bb);
  });
}
import type { NextApiRequest, NextApiResponse } from 'next';

const API_BASE_URL = process.env.API_BASE_URL;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Get the dynamic slug parts (e.g., ["map"] or ["mines", "1"])
  const { slug } = req.query;
  const targetPath = Array.isArray(slug) ? slug.join('/') : slug;
  const targetUrl = `${API_BASE_URL}/${targetPath}`;

  // Set up options for the proxied request.
  // Remove the host header since it should be determined by the target URL.
  const { method, headers } = req;
  const filteredHeaders = { ...headers };
  delete filteredHeaders.host;

  function toHeadersInit(headers: { [key: string]: string | string[] | undefined }): { [key: string]: string } {
    const result: { [key: string]: string } = {};
    for (const key in headers) {
      const value = headers[key];
      if (value === undefined) continue;
      result[key] = Array.isArray(value) ? value.join(', ') : value;
    }
    return result;
  }
  

  const options: RequestInit = {
    method,
    headers: toHeadersInit(filteredHeaders),
    body: ['GET', 'HEAD'].includes(method || '') ? undefined : JSON.stringify(req.body),
  };

  try {
    const response = await fetch(targetUrl, options);
    const contentType = response.headers.get('content-type');
    res.status(response.status);
    // Forward the content type header if available.
    if (contentType) res.setHeader('content-type', contentType);
    
    // If the response is JSON, parse and return it; otherwise, return as text.
    const data = contentType && contentType.includes('application/json')
      ? await response.json()
      : await response.text();
    
    res.send(data);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
}

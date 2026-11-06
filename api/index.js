/**
 * Vidi 4K Suite - Vercel Serverless Edge Handler
 * Provides dynamic Stremio search and Real-Debrid on-the-fly stream unrestrict.
 */

const UPSTREAM_BASE = "https://savad213.github.io/vidi-4k";
const DEFAULT_RD_KEY = "BFLGZUN4WH5FQQ3CBDAER6N7RH5EZNUFLVWQDNTB5A2JYDGVN4XA";

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "*");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const path = req.url || "/";
  const rdKey = process.env.RD_API_KEY || DEFAULT_RD_KEY;

  // 1. Stream handler with Real-Debrid dynamic renewal
  if (path.startsWith("/stream/movie/")) {
    try {
      const upstreamResp = await fetch(`${UPSTREAM_BASE}${path}`);
      if (!upstreamResp.ok) {
        return res.status(200).json({ streams: [] });
      }

      const streamData = await upstreamResp.json();
      const streams = streamData.streams || [];

      const resolvedStreams = await Promise.all(
        streams.map(async (st) => {
          if (st.url && st.url.includes("real-debrid.com/d/")) {
            try {
              const form = new URLSearchParams();
              form.append("link", st.url);

              const rdRes = await fetch("https://api.real-debrid.com/rest/1.0/unrestrict/link", {
                method: "POST",
                headers: {
                  "Authorization": `Bearer ${rdKey}`,
                  "Content-Type": "application/x-www-form-urlencoded"
                },
                body: form
              });

              if (rdRes.ok) {
                const rdData = await rdRes.json();
                if (rdData.download) {
                  return {
                    ...st,
                    url: rdData.download,
                    title: `⚡ 4K UHD Direct (Real-Debrid Fresh) - ${st.title || ""}`
                  };
                }
              }
            } catch (err) {
              console.error("RD unrestrict failed:", err);
            }
          }
          return st;
        })
      );

      return res.status(200).json({ streams: resolvedStreams });
    } catch (e) {
      return res.status(200).json({ streams: [] });
    }
  }

  // 2. Search Handler
  if (path.includes("/search=")) {
    try {
      const upstreamResp = await fetch(`${UPSTREAM_BASE}${path}`);
      if (upstreamResp.ok) {
        const data = await upstreamResp.json();
        return res.status(200).json(data);
      }
      return res.status(200).json({ metas: [] });
    } catch (e) {
      return res.status(200).json({ metas: [] });
    }
  }

  // 3. Upstream Passthrough
  try {
    const upstreamResp = await fetch(`${UPSTREAM_BASE}${path}`);
    const data = await upstreamResp.text();
    res.setHeader("Content-Type", upstreamResp.headers.get("content-type") || "application/json");
    return res.status(upstreamResp.status).send(data);
  } catch (e) {
    return res.status(502).json({ error: "Upstream fetch failed" });
  }
}

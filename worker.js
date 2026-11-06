/**
 * Vidi 4K Suite - Cloudflare Edge Worker
 * Provides dynamic Stremio search and Real-Debrid on-the-fly stream unrestrict.
 */

const UPSTREAM_BASE = "https://savad213.github.io/vidi-4k";
const DEFAULT_RD_KEY = "BFLGZUN4WH5FQQ3CBDAER6N7RH5EZNUFLVWQDNTB5A2JYDGVN4XA";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
  "Access-Control-Allow-Headers": "*",
  "Content-Type": "application/json; charset=utf-8"
};

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    const path = url.pathname;
    const rdKey = env?.RD_API_KEY || DEFAULT_RD_KEY;

    // 1. Dynamic Stream Handler (Unrestrict expired RD links on-the-fly)
    if (path.startsWith("/stream/movie/")) {
      const upstreamResp = await fetch(`${UPSTREAM_BASE}${path}`);
      if (!upstreamResp.ok) {
        return new Response(JSON.stringify({ streams: [] }), { headers: CORS_HEADERS });
      }

      const streamData = await upstreamResp.json();
      const streams = streamData.streams || [];

      // Check if any stream link is an expired/expiring Real-Debrid link
      const resolvedStreams = await Promise.all(
        streams.map(async (st) => {
          if (st.url && st.url.includes("real-debrid.com/d/")) {
            try {
              // Re-unrestrict via RD API to get a fresh streaming token
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
              console.error("RD Unrestrict error:", err);
            }
          }
          return st;
        })
      );

      return new Response(JSON.stringify({ streams: resolvedStreams }), { headers: CORS_HEADERS });
    }

    // 2. Dynamic Search Handler
    if (path.includes("/search=")) {
      const upstreamResp = await fetch(`${UPSTREAM_BASE}${path}`);
      if (upstreamResp.ok) {
        const body = await upstreamResp.text();
        return new Response(body, { headers: CORS_HEADERS });
      }

      // If pre-generated static search file was not found, return empty metas gracefully (prevents 404 in Stremio UI)
      return new Response(JSON.stringify({ metas: [] }), { headers: CORS_HEADERS });
    }

    // 3. Upstream passthrough for all other resources (manifest, catalog, meta)
    const upstreamResp = await fetch(`${UPSTREAM_BASE}${path}`);
    const headers = new Headers(upstreamResp.headers);
    headers.set("Access-Control-Allow-Origin", "*");
    return new Response(upstreamResp.body, {
      status: upstreamResp.status,
      headers
    });
  }
};

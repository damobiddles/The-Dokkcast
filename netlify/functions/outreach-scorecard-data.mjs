// Returns all saved reports (newest first) for the admin scorecard. GET /outreach-hq/scorecard/data
// Reached only through the admin password check in netlify/edge-functions/outreach-auth.ts.
import { getStore } from "@netlify/blobs";

export default async (req) => {
  if (req.method !== "GET") return new Response("Use GET", { status: 405 });
  const store = getStore({ name: "outreach-reports", consistency: "strong" });
  const { blobs } = await store.list();
  const keys = blobs.map((b) => b.key).sort().reverse().slice(0, 600);
  const reports = (await Promise.all(keys.map((k) => store.get(k, { type: "json" })))).filter(Boolean);
  return new Response(JSON.stringify({ reports }), { headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
};

export const config = { path: "/outreach-hq/scorecard/data" };

// Saves an end-of-day report from the Outreach HQ form into Netlify Blobs.
// POST /outreach-hq/api/report  (JSON). Reached only through the password check in netlify/edge-functions/outreach-auth.ts.
import { getStore } from "@netlify/blobs";

const PEOPLE = ["Katie", "Medha"];
const NUMS = ["igDms", "igComments", "ttComments", "ttDms", "replies", "interested"];
const FEEL = ["Easy", "Fine", "Too much"];
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });

export default async (req) => {
  if (req.method !== "POST") return json({ error: "Use POST" }, 405);
  let d;
  try { d = await req.json(); } catch { return json({ error: "Invalid JSON" }, 400); }
  if (!PEOPLE.includes(d.name)) return json({ error: "Unknown name" }, 400);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(d.date || "") || Number.isNaN(Date.parse(d.date))) return json({ error: "Bad date" }, 400);
  const report = { name: d.name, date: d.date };
  for (const k of NUMS) report[k] = Math.max(0, Math.min(99, parseInt(d[k], 10) || 0));
  report.leads = String(d.leads || "").trim().slice(0, 500);
  report.best = String(d.best || "").trim().slice(0, 1000);
  report.problems = String(d.problems || "").trim().slice(0, 1000);
  report.feel = FEEL.includes(d.feel) ? d.feel : "Fine";
  report.submittedAt = new Date().toISOString();
  await getStore({ name: "outreach-reports", consistency: "strong" }).setJSON(`${report.date}_${report.name}`, report);   // one report per person per day; resending replaces it
  return json({ ok: true });
};

export const config = { path: "/outreach-hq/api/report" };

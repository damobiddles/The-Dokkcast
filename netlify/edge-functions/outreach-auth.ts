// Password protection for the internal Outreach HQ page, its report endpoint and the admin scorecard.
//
// Two levels, both HTTP Basic auth (the browser shows its own login box):
//   - team:  /outreach-hq/*              any username + the password in OUTREACH_TEAM_PASSWORD
//   - admin: /outreach-hq/scorecard/*    a name + password pair listed in OUTREACH_ADMIN_USERS ("damien:pass1,partner:pass2")
// Admins can also open the team pages. Set both variables in Netlify (Site configuration > Environment variables).
// If a variable is missing, that level stays locked (nobody gets in), so a typo never opens the page up.
import type { Context } from "https://edge.netlify.com";

const enc = new TextEncoder();

// compare in constant time so response timing does not leak how much of a password matched
async function same(a: string, b: string): Promise<boolean> {
  const [ha, hb] = await Promise.all([crypto.subtle.digest("SHA-256", enc.encode(a)), crypto.subtle.digest("SHA-256", enc.encode(b))]);
  const x = new Uint8Array(ha), y = new Uint8Array(hb);
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

function parseBasic(req: Request): { user: string; pass: string } | null {
  const h = req.headers.get("authorization") || "";
  if (!h.toLowerCase().startsWith("basic ")) return null;
  try {
    const raw = atob(h.slice(6).trim());
    const i = raw.indexOf(":");
    return i < 0 ? null : { user: raw.slice(0, i), pass: raw.slice(i + 1) };
  } catch {
    return null;
  }
}

function deny(realm: string): Response {
  return new Response("Sign in to continue.", {
    status: 401,
    headers: { "WWW-Authenticate": `Basic realm="${realm}", charset="UTF-8"`, "Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow" },
  });
}

async function isAdmin(c: { user: string; pass: string } | null): Promise<boolean> {
  const list = (Netlify.env.get("OUTREACH_ADMIN_USERS") || "").split(",").map((s) => s.trim()).filter(Boolean);
  if (!c || !list.length) return false;
  let ok = false;
  for (const entry of list) {                      // check every entry so timing does not reveal which one matched
    const i = entry.indexOf(":");
    if (i < 1) continue;
    const userOk = await same(c.user.toLowerCase(), entry.slice(0, i).toLowerCase());
    const passOk = await same(c.pass, entry.slice(i + 1));
    if (userOk && passOk) ok = true;
  }
  return ok;
}

export default async (req: Request, context: Context) => {
  const path = new URL(req.url).pathname;
  const creds = parseBasic(req);
  const adminArea = path === "/outreach-hq/scorecard" || path.startsWith("/outreach-hq/scorecard/");

  if (adminArea) {
    return (await isAdmin(creds)) ? context.next() : deny("Udokk Outreach scorecard (admins)");
  }
  const teamPass = Netlify.env.get("OUTREACH_TEAM_PASSWORD") || "";
  if (creds && ((teamPass && (await same(creds.pass, teamPass))) || (await isAdmin(creds)))) return context.next();
  return deny("Udokk Outreach HQ");
};

export const config = { path: ["/outreach-hq", "/outreach-hq/*"] };

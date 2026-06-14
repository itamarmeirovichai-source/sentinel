// Cloudflare Pages "advanced mode" Worker: runs for every request before static assets.
// Enforces HTTP Basic Auth using the SITE_PASSWORD secret (set on the Pages project).
// The password is NOT in this file. Fail-closed: missing/blank secret => locked.
export default {
  async fetch(request, env) {
    const expected = env.SITE_PASSWORD;

    const header = request.headers.get("Authorization") || "";
    let provided = null;
    if (header.startsWith("Basic ")) {
      try {
        const decoded = atob(header.slice(6));              // "username:password"
        provided = decoded.slice(decoded.indexOf(":") + 1);  // ignore username, take password
      } catch (_e) {
        provided = null;
      }
    }

    if (!expected || provided !== expected) {
      return new Response("Authentication required.", {
        status: 401,
        headers: { "WWW-Authenticate": 'Basic realm="Sentinel (private)", charset="UTF-8"' },
      });
    }

    return env.ASSETS.fetch(request); // authenticated -> serve the static landing page
  },
};

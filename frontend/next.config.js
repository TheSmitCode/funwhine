// next.config.js
/**
 * Development helper: rewrites requests from `/api/*` to your backend.
 * This makes the browser treat Next dev server and backend as same-origin
 * (so cookies set by backend will be sent automatically), simplifying dev.
 *
 * Production: remove this rewrite and set NEXT_PUBLIC_API_BASE to your real API origin,
 * or use a proper reverse proxy (nginx) to serve both frontend & backend under same origin.
 */
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/v1/:path*' // <-- change if backend runs elsewhere
      }
    ]
  },
};

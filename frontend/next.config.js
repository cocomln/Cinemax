/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**" },
      { protocol: "http", hostname: "**" },
    ],
  },
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL;
    if (backendUrl) {
      const cleanUrl = backendUrl.replace(/\/+$/, "");
      const destination = cleanUrl.endsWith("/api")
        ? `${cleanUrl}/:path*`
        : `${cleanUrl}/api/:path*`;
      return [
        {
          source: "/api/:path*",
          destination,
        },
      ];
    }
    return [];
  },
};

module.exports = nextConfig;

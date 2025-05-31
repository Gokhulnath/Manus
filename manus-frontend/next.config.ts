import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    // Disable lightningcss to avoid native binary issue
    optimizeCss: false,
  },
};

export default nextConfig;

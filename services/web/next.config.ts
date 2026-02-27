import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  eslint: {
    // Disable ESLint during build (will still run in dev)
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable TypeScript checks during build (will still run in dev)
    ignoreBuildErrors: true,
  },
};

export default nextConfig;

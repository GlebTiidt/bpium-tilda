import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Mount app under /application for Webflow Cloud
  basePath: "/application",
  assetPrefix: "/application",
  // Write build output to a custom folder (avoid locked .next)
  distDir: ".wf-next",
};

export default nextConfig;

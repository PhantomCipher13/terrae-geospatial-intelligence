/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || "https://terrae-backend.onrender.com",
  },
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;

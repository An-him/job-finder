/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:5000/api/:path*',
      },
    ]
  },
  async redirects() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:5000/api/:path*',
        permanent: true,
      },
    ]
  },
}

export default nextConfig
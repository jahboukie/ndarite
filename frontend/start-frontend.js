#!/usr/bin/env node
/**
 * NDARite Frontend Startup Script
 * This script starts the Next.js development server
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Starting NDARite Frontend...');
console.log('📍 Frontend will be available at: http://localhost:3000');
console.log('🔗 Backend API at: http://localhost:8000');
console.log('🔄 Press Ctrl+C to stop\n');

// Set environment variables
process.env.NODE_ENV = 'development';
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000/api/v1';
process.env.NEXT_PUBLIC_APP_URL = 'http://localhost:3000';

// Start Next.js development server
const nextPath = path.join(__dirname, 'node_modules', 'next', 'dist', 'bin', 'next');
const args = ['dev', '--port', '3000'];

console.log(`Running: node ${nextPath} ${args.join(' ')}`);

const child = spawn('node', [nextPath, ...args], {
  stdio: 'inherit',
  cwd: __dirname,
  env: process.env
});

child.on('error', (error) => {
  console.error('❌ Failed to start frontend:', error.message);
  process.exit(1);
});

child.on('close', (code) => {
  console.log(`\n👋 Frontend server stopped with code ${code}`);
  process.exit(code);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down frontend server...');
  child.kill('SIGINT');
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Shutting down frontend server...');
  child.kill('SIGTERM');
});

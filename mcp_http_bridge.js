#!/usr/bin/env node
/**
 * MCP HTTP Bridge - Converts stdio MCP protocol to HTTP/WebSocket
 * 
 * Usage:
 *   MCP_SERVER_URL=http://192.168.4.208:8000 node mcp_http_bridge.js
 * 
 * Or configure in ~/.cursor/mcp.json:
 * {
 *   "mcpServers": {
 *     "xcode-mcp-remote": {
 *       "command": "node",
 *       "args": ["/path/to/mcp_http_bridge.js"],
 *       "env": {
 *         "MCP_SERVER_URL": "http://192.168.4.208:8000",
 *         "MCP_API_KEY": ""
 *       }
 *     }
 *   }
 * }
 */

const WebSocket = require('ws');
const readline = require('readline');

const SERVER_URL = process.env.MCP_SERVER_URL || 'http://192.168.4.208:8000';
const API_KEY = process.env.MCP_API_KEY || '';

// Parse server URL
let wsUrl;
try {
  const url = new URL(SERVER_URL);
  wsUrl = `ws://${url.hostname}:${url.port}/ws${API_KEY ? `?api_key=${API_KEY}` : ''}`;
} catch (e) {
  console.error('Invalid MCP_SERVER_URL:', SERVER_URL);
  process.exit(1);
}

// Create WebSocket connection
const ws = new WebSocket(wsUrl);

// Read from stdin (MCP requests)
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

let connected = false;
const messageQueue = [];

ws.on('open', () => {
  connected = true;
  console.error('✅ Connected to MCP server:', SERVER_URL);
  
  // Send queued messages
  while (messageQueue.length > 0) {
    ws.send(messageQueue.shift());
  }
  
  // Forward stdin to WebSocket
  rl.on('line', (line) => {
    if (line.trim()) {
      try {
        if (connected) {
          ws.send(line);
        } else {
          messageQueue.push(line);
        }
      } catch (e) {
        console.error('Error sending:', e);
      }
    }
  });
});

// Forward WebSocket messages to stdout (MCP responses)
ws.on('message', (data) => {
  try {
    const message = data.toString();
    process.stdout.write(message + '\n');
    process.stdout.flush();
  } catch (e) {
    console.error('Error writing to stdout:', e);
  }
});

ws.on('error', (error) => {
  console.error('❌ WebSocket error:', error.message);
  if (!connected) {
    console.error('   Make sure the server is running at:', SERVER_URL);
    console.error('   Start server with: python run_network_server.py');
  }
  process.exit(1);
});

ws.on('close', (code, reason) => {
  console.error('🔌 Connection closed:', reason || code);
  process.exit(0);
});

// Handle stdin end
process.stdin.on('end', () => {
  if (connected) {
    ws.close();
  }
});

// Handle process termination
process.on('SIGINT', () => {
  if (connected) {
    ws.close();
  }
  process.exit(0);
});

process.on('SIGTERM', () => {
  if (connected) {
    ws.close();
  }
  process.exit(0);
});



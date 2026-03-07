const express = require('express');
const path = require('path');
const fs = require('fs');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 3000;

// Proxy /api requests to backend
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:8001',
  changeOrigin: true,
}));

// Serve static files from build directory
const buildPath = path.join(__dirname, 'build');
app.use(express.static(buildPath));

// Handle all other routes - serve index.html for SPA
app.use((req, res) => {
  const requestPath = req.path;
  
  // Check if there's a specific HTML file for this route (Expo static export)
  const htmlPath = path.join(buildPath, requestPath + '.html');
  const indexPath = path.join(buildPath, requestPath, 'index.html');
  const directPath = path.join(buildPath, requestPath);
  
  if (fs.existsSync(htmlPath)) {
    res.sendFile(htmlPath);
  } else if (fs.existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else if (fs.existsSync(directPath) && fs.statSync(directPath).isFile()) {
    res.sendFile(directPath);
  } else {
    // Default to main index.html for client-side routing
    res.sendFile(path.join(buildPath, 'index.html'));
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`NeoChef PWA server running on port ${PORT}`);
});

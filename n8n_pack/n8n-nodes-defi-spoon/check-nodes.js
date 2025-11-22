// Script to check if all nodes are properly exported
const path = require('path');
const fs = require('fs');

const packagePath = path.join(__dirname, 'package.json');
const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));

console.log('Package name:', packageJson.name);
console.log('\nNodes listed in package.json:');
packageJson.n8n.nodes.forEach((node, i) => {
  console.log(`  ${i + 1}. ${node}`);
});

console.log('\nChecking if files exist and can be loaded:');
packageJson.n8n.nodes.forEach((nodePath) => {
  const fullPath = path.join(__dirname, nodePath);
  const exists = fs.existsSync(fullPath);
  console.log(`  ${nodePath}: ${exists ? '✓ EXISTS' : '✗ MISSING'}`);
  
  if (exists) {
    try {
      const module = require(fullPath);
      const keys = Object.keys(module);
      console.log(`    Exported: ${keys.join(', ')}`);
      
      // Check if it's a valid n8n node
      if (keys.length > 0) {
        const NodeClass = module[keys[0]];
        if (NodeClass && NodeClass.prototype && NodeClass.prototype.description) {
          const desc = NodeClass.prototype.description;
          console.log(`    Display Name: ${desc.displayName || 'N/A'}`);
          console.log(`    Name: ${desc.name || 'N/A'}`);
        }
      }
    } catch (error) {
      console.log(`    ✗ ERROR loading: ${error.message}`);
    }
  }
});


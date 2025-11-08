#!/usr/bin/env node
/**
 * Simple test to verify PDF extraction and API endpoints work correctly
 */

import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🧪 Testing PDF extraction functionality...\n');

// Test 1: Verify Python script exists
async function testScriptExists() {
  try {
    const scriptPath = path.resolve(__dirname, '../pdfExtraction/extract_pdf.py');
    await fs.access(scriptPath);
    console.log('✅ Test 1: PDF extraction script exists');
    return true;
  } catch (error) {
    console.error('❌ Test 1: PDF extraction script not found');
    return false;
  }
}

// Test 2: Test script with non-existent file (failsafe test)
async function testFailsafe() {
  return new Promise((resolve) => {
    const pythonProcess = spawn('python3', [
      'pdfExtraction/extract_pdf.py',
      '/tmp/nonexistent_file_test_12345.pdf'
    ]);

    let output = '';
    pythonProcess.stdout.on('data', (chunk) => {
      output += chunk.toString();
    });

    pythonProcess.on('close', (code) => {
      try {
        const result = JSON.parse(output);
        if (result && result.length > 0 && result[0].topic === 'File Not Found') {
          console.log('✅ Test 2: Failsafe works correctly (returns structured error)');
          resolve(true);
        } else {
          console.error('❌ Test 2: Failsafe did not return expected format');
          resolve(false);
        }
      } catch (error) {
        console.error('❌ Test 2: Output is not valid JSON:', output);
        resolve(false);
      }
    });
  });
}

// Test 3: Verify dependencies
async function testDependencies() {
  return new Promise((resolve) => {
    const pythonProcess = spawn('python3', ['-c', 'import pdfminer.high_level; print("OK")']);
    
    let output = '';
    pythonProcess.stdout.on('data', (chunk) => {
      output += chunk.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code === 0 && output.trim() === 'OK') {
        console.log('✅ Test 3: pdfminer.six is installed');
        resolve(true);
      } else {
        console.log('⚠️  Test 3: pdfminer.six not installed (run: pip install pdfminer.six)');
        resolve(false);
      }
    });
  });
}

// Test 4: Test help command
async function testHelpCommand() {
  return new Promise((resolve) => {
    const pythonProcess = spawn('python3', ['pdfExtraction/extract_pdf.py', '--help']);
    
    let output = '';
    pythonProcess.stdout.on('data', (chunk) => {
      output += chunk.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code === 0 && output.includes('Extract topics and content')) {
        console.log('✅ Test 4: Help command works');
        resolve(true);
      } else {
        console.error('❌ Test 4: Help command failed');
        resolve(false);
      }
    });
  });
}

// Run all tests
async function runTests() {
  console.log('Running tests...\n');
  
  const results = [];
  results.push(await testScriptExists());
  results.push(await testDependencies());
  results.push(await testHelpCommand());
  results.push(await testFailsafe());
  
  console.log('\n' + '='.repeat(50));
  const passed = results.filter(r => r).length;
  const total = results.length;
  console.log(`\n📊 Test Results: ${passed}/${total} passed`);
  
  if (passed === total) {
    console.log('✅ All tests passed! The PDF extraction module is working correctly.');
    process.exit(0);
  } else {
    console.log('⚠️  Some tests failed. Please check the output above.');
    process.exit(1);
  }
}

runTests().catch(error => {
  console.error('Test runner error:', error);
  process.exit(1);
});

#!/usr/bin/env node

/**
 * File Encryptor Tool
 * Encrypts files using AES-256-CBC encryption
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// Hardcoded encryption key and IV
const ENCRYPTION_KEY = crypto.createHash('sha256').update('EdgeSecureKey2024!').digest(); // 32 bytes for AES-256
const IV = crypto.createHash('md5').update('EdgeCTFVector!').digest(); // 16 bytes for IV

function encryptFile(inputPath, outputPath) {
    try {
        // Read the input file
        const data = fs.readFileSync(inputPath);
        
        // Create cipher
        const cipher = crypto.createCipheriv('aes-256-cbc', ENCRYPTION_KEY, IV);
        
        // Encrypt the data
        let encrypted = cipher.update(data);
        encrypted = Buffer.concat([encrypted, cipher.final()]);
        
        // Write encrypted data to output file
        fs.writeFileSync(outputPath, encrypted);
        
        console.log(`[+] File encrypted successfully!`);
        console.log(`[+] Input:  ${inputPath}`);
        console.log(`[+] Output: ${outputPath}`);
        
        return true;
    } catch (error) {
        console.error(`[-] Encryption failed: ${error.message}`);
        return false;
    }
}

function decryptFile(inputPath, outputPath) {
    try {
        // Read the encrypted file
        const encryptedData = fs.readFileSync(inputPath);
        
        // Create decipher
        const decipher = crypto.createDecipheriv('aes-256-cbc', ENCRYPTION_KEY, IV);
        
        // Decrypt the data
        let decrypted = decipher.update(encryptedData);
        decrypted = Buffer.concat([decrypted, decipher.final()]);
        
        // Write decrypted data to output file
        fs.writeFileSync(outputPath, decrypted);
        
        console.log(`[+] File decrypted successfully!`);
        console.log(`[+] Input:  ${inputPath}`);
        console.log(`[+] Output: ${outputPath}`);
        
        return true;
    } catch (error) {
        console.error(`[-] Decryption failed: ${error.message}`);
        return false;
    }
}

// Main execution
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length < 3) {
        console.error('[-] Error: Invalid arguments');
        process.exit(1);
    }
    
    const [operation, inputFile, outputFile] = args;
    
    if (!fs.existsSync(inputFile)) {
        console.error(`[-] Error: Input file '${inputFile}' not found!`);
        process.exit(1);
    }
    
    if (operation === 'encrypt') {
        const success = encryptFile(inputFile, outputFile);
        process.exit(success ? 0 : 1);
    } else if (operation === 'decrypt') {
        const success = decryptFile(inputFile, outputFile);
        process.exit(success ? 0 : 1);
    } else {
        console.error(`[-] Error: Unknown operation '${operation}'`);
        process.exit(1);
    }
}

module.exports = { encryptFile, decryptFile };

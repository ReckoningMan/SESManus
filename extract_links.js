const fs = require('fs');
const path = require('path');

const inputFile = path.join(__dirname, 'Quick Reference Guides single file.mhtml');
const outputFile = path.join(__dirname, 'pdf_links_final.txt');

// Read the file
fs.readFile(inputFile, 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading file:', err);
        return;
    }

    // Extract all PDF links using a more permissive regex
    const pdfLinks = [];
    const regex = /https?:\/\/[^\s"'<>]+?\.pdf/gi;
    let match;
    
    while ((match = regex.exec(data)) !== null) {
        const link = match[0];
        // Clean up the link
        const cleanLink = link
            .replace(/["']$/, '')  // Remove trailing quotes
            .replace(/\\/g, '/')   // Fix backslashes
            .trim();
            
        if (!pdfLinks.includes(cleanLink)) {
            pdfLinks.push(cleanLink);
        }
    }

    // Write the links to the output file
    fs.writeFileSync(outputFile, pdfLinks.join('\n'), 'utf8');
    
    console.log(`Found ${pdfLinks.length} unique PDF links.`);
    console.log('First 5 links:');
    pdfLinks.slice(0, 5).forEach((link, i) => console.log(`${i + 1}. ${link}`));
    console.log(`\nAll links have been saved to: ${outputFile}`);
});

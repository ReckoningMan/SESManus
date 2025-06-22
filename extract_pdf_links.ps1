$inputFile = "Quick Reference Guides single file.mhtml"
$outputFile = "pdf_links.txt"

# Read the file content
$content = Get-Content -Path $inputFile -Raw -Encoding UTF8

# Find all PDF links using regex
$pattern = 'https?://[^\s"\'<>]+?\.pdf'
$matches = [regex]::Matches($content, $pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)

# Extract unique links and clean them up
$uniqueLinks = @{}
foreach ($match in $matches) {
    $cleanLink = $match.Value.Trim()
    $cleanLink = [System.Web.HttpUtility]::UrlDecode($cleanLink)
    if (-not $uniqueLinks.ContainsKey($cleanLink)) {
        $uniqueLinks[$cleanLink] = $true
    }
}

# Write the links to the output file
$uniqueLinks.Keys | Out-File -FilePath $outputFile -Encoding utf8

# Display results
Write-Host "Found $($uniqueLinks.Count) unique PDF links. Saved to: $outputFile"
Write-Host "`nFirst 5 links:"
$($uniqueLinks.Keys | Select-Object -First 5 | ForEach-Object { "- $_" })

param(
    [string]$pptxPath = "c:\Users\Admin\Downloads\Internal hackathon\TERRAE_SIH2026_Presentation.pptx",
    [string]$outDir = "C:\Users\Admin\.gemini\antigravity\brain\d1a1e5ad-c438-4104-985b-ec757632f80e\sih_slides"
)

if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$ppt = New-Object -ComObject PowerPoint.Application
try {
    $presentation = $ppt.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    $slideCount = $presentation.Slides.Count
    Write-Host "Exporting $slideCount slides to PNG in $outDir..."

    for ($i = 1; $i -le $slideCount; $i++) {
        $outPath = Join-Path $outDir "SLIDE_$($i.ToString('D2')).png"
        $presentation.Slides.Item($i).Export($outPath, "PNG", 1920, 1080)
        Write-Host "Exported Slide $i -> $outPath"
    }
    $presentation.Close()
}
finally {
    $ppt.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
}
Write-Host "Export complete!"

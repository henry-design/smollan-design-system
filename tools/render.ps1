# Render every slide of a .pptx to PNG through PowerPoint (Windows + Office required).
#   powershell -File tools\render.ps1 -Pptx examples\deck.pptx -Out out_dir [-Width 800]
#   add -Pdf to also save a PDF next to the deck
param(
  [Parameter(Mandatory = $true)][string]$Pptx,
  [Parameter(Mandatory = $true)][string]$Out,
  [int]$Width = 800,
  [switch]$Pdf
)
$Pptx = (Resolve-Path $Pptx).Path
New-Item -ItemType Directory -Force $Out | Out-Null
$Out = (Resolve-Path $Out).Path
$ppt = New-Object -ComObject PowerPoint.Application
try {
  $p = $ppt.Presentations.Open($Pptx, -1, 0, 0)
  $h = [int]($Width * 9 / 16)
  for ($i = 1; $i -le $p.Slides.Count; $i++) {
    $name = $p.Slides.Item($i).Name -replace '[^\w\.\-]', '_'
    $p.Slides.Item($i).Export((Join-Path $Out ('{0:D3}_{1}.png' -f $i, $name)), "PNG", $Width, $h)
  }
  if ($Pdf) { $p.SaveAs(([IO.Path]::ChangeExtension($Pptx, ".pdf")), 32) }
  "rendered $($p.Slides.Count) slides to $Out"
  $p.Close()
} finally { $ppt.Quit() }

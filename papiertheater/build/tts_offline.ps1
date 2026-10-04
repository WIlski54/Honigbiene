# Offline-Ersatz für die Sprecherin: Windows-Stimme "Katja" (OneCore, 16 kHz, klingt blecherner als edge-tts).
# Aufruf: powershell -ExecutionPolicy Bypass -File build\tts_offline.ps1 [-Rate 0.92] [-Only 3]
# Schreibt assets\voice\sceneNN.wav, aber keine Satz-Zeitmarken. Danach: python build\cues_offline.py, dann make_audio.py.
param([double]$Rate = 0.92, [int]$Only = 0)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$outDir = Join-Path $root 'assets\voice'
New-Item -ItemType Directory -Force $outDir | Out-Null
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media.SpeechSynthesis, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.DataReader, Windows.Storage.Streams, ContentType = WindowsRuntime]
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, [Type]$type) { $t = $asTaskGeneric.MakeGenericMethod($type).Invoke($null, @($op)); $t.Wait(-1) | Out-Null; $t.Result }
$synth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
$synth.Voice = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object { $_.DisplayName -like '*Katja*' } | Select-Object -First 1
$synth.Options.SpeakingRate = $Rate
$json = Get-Content -Raw -Encoding UTF8 (Join-Path $PSScriptRoot 'narration.json') | ConvertFrom-Json
foreach ($s in $json.szenen) {
  if ($Only -ne 0 -and $s.id -ne $Only) { continue }
  $text = [string]$s.text
  if ($json.aussprache) { foreach ($p in $json.aussprache.PSObject.Properties) { $text = $text.Replace($p.Name, $p.Value) } }
  $text = [System.Security.SecurityElement]::Escape($text) -replace '([.!?]) ', '$1 <break time="450ms"/> '
  $ssml = "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='de-DE'>$text</speak>"
  $stream = Await ($synth.SynthesizeSsmlToStreamAsync($ssml)) ([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
  $reader = New-Object Windows.Storage.Streams.DataReader($stream.GetInputStreamAt(0))
  $n = Await ($reader.LoadAsync([uint32]$stream.Size)) ([uint32])
  $bytes = New-Object byte[] $n; $reader.ReadBytes($bytes)
  [IO.File]::WriteAllBytes((Join-Path $outDir ('scene{0:D2}.wav' -f [int]$s.id)), $bytes)
  Write-Output ('Szene {0}: {1} Bytes' -f $s.id, $n)
}

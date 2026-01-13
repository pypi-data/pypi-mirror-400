param(
    [string]$CommitMsgFile
)

if (-not $CommitMsgFile) {
    Write-Error "Uso: commit-msg.ps1 <arquivo>"
    exit 1
}

$firstLine = Get-Content -Path $CommitMsgFile -TotalCount 1

$regex = '^(feat|fix|test|chore|docs|refactor|perf|ci|build|revert)(\([^)]+\))?: .+'

if ($firstLine -notmatch $regex) {
    Write-Host "Mensagem de commit inválida.`nFormato esperado: <tipo>(escopo-opcional): descrição curta em pt-BR" -ForegroundColor Red
    Write-Host "Tipos permitidos: feat, fix, test, chore, docs, refactor, perf, ci, build, revert" -ForegroundColor Red
    exit 1
}

exit 0

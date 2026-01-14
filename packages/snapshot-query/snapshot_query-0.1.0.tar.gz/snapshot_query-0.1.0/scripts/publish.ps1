# PowerShell 发布脚本

Write-Host "🧹 清理旧的构建文件..." -ForegroundColor Cyan
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist, build, *.egg-info

Write-Host "📦 构建分发包..." -ForegroundColor Cyan
python -m build

Write-Host "✅ 检查分发包..." -ForegroundColor Cyan
twine check dist/*

Write-Host "📤 准备发布..." -ForegroundColor Green
Write-Host "要发布到 TestPyPI，运行:" -ForegroundColor Yellow
Write-Host "  twine upload --repository testpypi dist/*" -ForegroundColor White
Write-Host ""
Write-Host "要发布到 PyPI，运行:" -ForegroundColor Yellow
Write-Host "  twine upload dist/*" -ForegroundColor White

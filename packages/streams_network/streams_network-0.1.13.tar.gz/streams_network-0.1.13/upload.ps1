maturin build --release --sdist --out dist
$env:UV_PUBLISH_TOKEN="pypi-xxxxxxxxxxxxxxxx"

uv publish dist/*

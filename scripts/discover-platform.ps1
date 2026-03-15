Set-Location $PSScriptRoot\..
py -c "from validator_engine.engine import ValidationEngine; print(ValidationEngine().discover_architecture())"

"""Use the upstream-recommended drive-root checkout and preserve build state."""
from pathlib import Path
import yaml

path = Path('.github/workflows/windows.yml')
workflow = yaml.safe_load(path.read_text(encoding='utf-8'))
if True in workflow:
    workflow['on'] = workflow.pop(True)
steps = workflow['jobs']['build']['steps']
updated = []
for step in steps:
    name = step.get('name', '')
    if name == 'Check out official Open RV 4.0.2':
        step = {
            'name': name,
            'shell': 'pwsh',
            'run': '''
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath 'D:\\rv') { throw 'Expected a fresh D:\\rv checkout' }
git -c core.longpaths=true clone --branch v4.0.2 --depth 1 --recurse-submodules --shallow-submodules https://github.com/AcademySoftwareFoundation/OpenRV.git D:\\rv
if ($LASTEXITCODE -ne 0) { throw 'Official source clone failed' }
$actualCommit = git -C D:\\rv rev-parse HEAD
if ($actualCommit.Trim() -ne '27db5464a90ca19a9a30d540988ee109ee06bb7e') { throw 'Unexpected source commit' }
Write-Output "Verified official source commit: $actualCommit"
'''
        }
    if step.get('working-directory') == '${{ github.workspace }}/source':
        step['working-directory'] = 'D:/rv'
    if name == 'Configure OpenRV':
        updated.append({
            'name': 'Restore previous dependency build',
            'id': 'deps-cache',
            'uses': 'actions/cache/restore@v4',
            'with': {
                'path': 'D:/rv/_build',
                'key': 'openrv-402-win1440-prores-short-v1-${{ github.run_id }}-${{ github.run_attempt }}',
                'restore-keys': 'openrv-402-win1440-prores-short-v1-'
            }
        })
        step['id'] = 'configure'
    if name == 'Verify packaged codecs':
        step['run'] = 'python builder/verify.py D:/rv/_install'
    if name == 'Upload portable Windows build':
        step['with']['path'] = 'D:/rv/_install/'
    if name == 'Upload diagnostic logs':
        step['with']['path'] = '\n'.join([
            'D:/rv-configure.log', 'D:/rv-dependencies.log', 'D:/rv-main.log',
            'D:/rv/_build/CMakeCache.txt',
            'D:/rv/_build/CMakeFiles/CMakeConfigureLog.yaml'
        ])
    if name in ('Configure OpenRV', 'Build OpenRV dependencies', 'Build OpenRV main executable'):
        log_name = {'Configure OpenRV': 'configure', 'Build OpenRV dependencies': 'dependencies',
                    'Build OpenRV main executable': 'main'}[name]
        lines = step['run'].splitlines()
        lines = [line + f' 2>&1 | tee /d/rv-{log_name}.log' if line.startswith('cmake -') else line for line in lines]
        step['run'] = 'set -o pipefail\n' + '\n'.join(lines) + '\n'
    updated.append(step)
updated.append({
    'name': 'Save dependency build for subsequent runs',
    'if': "always() && steps.configure.outcome == 'success'",
    'continue-on-error': True,
    'uses': 'actions/cache/save@v4',
    'with': {
        'path': 'D:/rv/_build',
        'key': '${{ steps.deps-cache.outputs.cache-primary-key }}'
    }
})
workflow['jobs']['build']['steps'] = updated
path.write_text(yaml.safe_dump(workflow, sort_keys=False, width=140), encoding='utf-8')
print('Workflow uses D:/rv, explicit log files, and a reusable dependency cache.')

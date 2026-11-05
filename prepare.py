"""Adapt the upstream composite action without modifying application source."""
from pathlib import Path
import sys
import yaml

root = Path(sys.argv[1])
path = root / '.github/actions/build-windows/action.yml'
action = yaml.safe_load(path.read_text(encoding='utf-8'))
for step in action['runs']['steps']:
    if 'run' not in step:
        continue
    step['working-directory'] = '${{ github.workspace }}/source'
    if step.get('name') == 'Set PATH environment variable':
        step['run'] = '''
python_dir=$(cygpath -u "$pythonLocation")
echo "export PATH=\\\"/c/Program Files/CMake/bin:$python_dir:/c/msys64/mingw64/bin:\\$PATH:/c/Strawberry/c/bin:/c/Strawberry/perl/site/bin:/c/Strawberry/perl/bin:/c/ProgramData/Chocolatey/bin:/c/ProgramData/Chocolatey/lib/jom/tools\\\"" >> ~/.bash_profile
'''
    if step.get('name') == 'Configure OpenRV':
        step['run'] += '\n'
        step['run'] = step['run'].replace(
            '-DRV_VFX_PLATFORM=${{ inputs.vfx-platform }}',
            '-DRV_VFX_PLATFORM=${{ inputs.vfx-platform }} '
            "'-DRV_FFMPEG_NON_FREE_DECODERS_TO_ENABLE=prores;aac;aac_fixed;aac_latm'"
        )
        # Match the upstream MSVC 14.40 toolchain selected above.
        step['run'] = step['run'].replace('-A x64 ', '-A x64 -T v143,version=14.40 ')
    if step.get('name') == 'Install CMake ${{ inputs.cmake-version }} with chocolatey':
        step['run'] += ' --yes'
    if step.get('shell', '').startswith('msys2'):
        step['run'] = '''
source ~/.bash_profile
python_dir=$(cygpath -u "$pythonLocation")
msvc_bin=$(cygpath -u "${VCToolsInstallDir}bin/Hostx64/x64")
export PATH="$msvc_bin:/c/Program Files/CMake/bin:$python_dir:$python_dir/Scripts:/mingw64/bin:$PATH:/c/Strawberry/c/bin:/c/Strawberry/perl/site/bin:/c/Strawberry/perl/bin:/c/Users/runneradmin/.cargo/bin:/c/ProgramData/Chocolatey/bin:/c/ProgramData/Chocolatey/lib/jom/tools"
export ACLOCAL_PATH=/usr/share/aclocal
export WIN_PYTHON_DIR="$pythonLocation"
''' + step['run'].replace('python3 -m pip', 'python -m pip')
    if step.get('name') == 'Install Qt ${{ inputs.qt-version }}':
        step['with']['cache'] = True
path.write_text(yaml.safe_dump(action, sort_keys=False, width=120), encoding='utf-8')
print('Prepared upstream build action: ProRes/AAC enabled; official source unchanged.')

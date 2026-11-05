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
python_dir=$(cygpath -u "$(python -c 'import sys,os; print(os.path.dirname(sys.executable))')")
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
path.write_text(yaml.safe_dump(action, sort_keys=False, width=120), encoding='utf-8')
print('Prepared upstream build action: ProRes/AAC enabled; official source unchanged.')

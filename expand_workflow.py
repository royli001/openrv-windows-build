"""Expose upstream composite steps individually for live Actions progress."""
from pathlib import Path
import yaml

path = Path('.github/workflows/windows.yml')
workflow = yaml.safe_load(path.read_text(encoding='utf-8'))
if True in workflow:
    workflow['on'] = workflow.pop(True)
original = workflow['jobs']['build']['steps']
marker = next(s for s in original if s.get('uses') == './source/.github/actions/build-windows')
values = marker['with']
action = yaml.safe_load(Path('validation/.github/actions/build-windows/action.yml').read_text(encoding='utf-8'))
for key, spec in action['inputs'].items():
    values.setdefault(key, spec.get('default'))
def substitute(value):
    if isinstance(value, str):
        for key, replacement in values.items():
            value = value.replace('${{ inputs.' + key + ' }}', str(replacement))
        return value
    if isinstance(value, list):
        return [substitute(item) for item in value]
    if isinstance(value, dict):
        return {key: substitute(item) for key, item in value.items()}
    return value
expanded = substitute(action['runs']['steps'])
steps = []
for step in original:
    if step.get('name') == 'Prepare official build action':
        continue
    if step is marker:
        steps.extend(expanded)
    else:
        steps.append(step)
workflow['jobs']['build']['steps'] = steps
path.write_text(yaml.safe_dump(workflow, sort_keys=False, width=140), encoding='utf-8')
print(f'Expanded {len(expanded)} official build steps.')

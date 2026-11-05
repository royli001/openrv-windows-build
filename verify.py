"""Require real decoders in the packaged FFmpeg library before publishing an artifact."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
rv = list(root.rglob('rv.exe'))
assert rv, f'No rv.exe found in {root}'
dlls = list(root.rglob('avcodec-*.dll'))
assert dlls, 'No avcodec DLL found'
handles = [os.add_dll_directory(str(p)) for p in {p.parent for p in root.rglob('*.dll')}]
lib = ctypes.CDLL(str(dlls[0]))
lib.avcodec_find_decoder_by_name.argtypes = [ctypes.c_char_p]
lib.avcodec_find_decoder_by_name.restype = ctypes.c_void_p
lib.avcodec_configuration.restype = ctypes.c_char_p
codecs = {name: bool(lib.avcodec_find_decoder_by_name(name.encode())) for name in ['prores', 'aac', 'h264']}
assert all(codecs.values()), f'Missing required decoder: {codecs}'
report = {'upstream': 'AcademySoftwareFoundation/OpenRV', 'version': '4.0.2',
          'commit': '27db5464a90ca19a9a30d540988ee109ee06bb7e', 'decoders': codecs,
          'ffmpeg_config': lib.avcodec_configuration().decode(),
          'rv_sha256': hashlib.sha256(rv[0].read_bytes()).hexdigest()}
(root / 'BUILD-INFO.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))

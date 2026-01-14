import shutil
from pathlib import Path
from ls_buildtools._integration import BUILDTOOLS_CONFIG_FILE
from ls_buildtools.protect import Protector
from ls_buildtools.protector_config import ProtectorConfig
from ls_buildtools.utilities import read_protector_config
try:
	from setuptools.command.sdist import sdist
	class ProtectionCommand(sdist):
		def make_release_tree(F,base_dir,files):
			A=base_dir;super().make_release_tree(A,files);print('Protecting files with LocalStack BuildTools protection...');A=Path(A);G=A/'setup.py';G.unlink();H:ProtectorConfig=read_protector_config(A/'..'/BUILDTOOLS_CONFIG_FILE);I=A/BUILDTOOLS_CONFIG_FILE;I.unlink(missing_ok=True);J=F.distribution.get_version();E=Protector();E.initialize(version=J,config=H)
			for K in A.rglob('*'):
				B=Path(K)
				if B.is_file():
					print(f"- Protecting file: {B}");C,D=E.protect_file(B,B)
					if D is not None:
						if C.absolute()!=B.absolute():B.unlink()
						if D.absolute()!=C.absolute():shutil.move(C.absolute(),D.absolute())
					else:B.unlink();C.unlink(missing_ok=True)
except ImportError:pass
import os, re, subprocess, tempfile

from IPython.display import HTML, Image
from metakernel import MetaKernel, Magic

class GPPMagics(Magic):
  def line_CC(self, a=''):
    self.kernel._vars["CC"] = a

  def line_CFLAGS(self, a=''):
    self.kernel._vars["CFLAGS"] = a

  def line_CPPFLAGS(self, a=''):
    self.kernel._vars["CPPFLAGS"] = a

  def line_LDFLAGS(self, a=''):
    self.kernel._vars["LDFLAGS"] = a

  def line_OFLAGS(self, a=''):
    self.kernel._vars["OFLAGS"] = a

  def line_PFLAGS(self, a=''):
    self.kernel._vars["PFLAGS"] = a

  def line_C(self, a=''):
    self.kernel._cellcontents = "c"

  def line_OCTAVE(self, a=''):
    self.kernel._cellcontents = "octave"

  def line_PUML(self, a=''):
    self.kernel._cellcontents = "puml"

  def line_cd(self, a=''):
    os.chdir(os.path.expanduser(a)) if a and os.path.isdir(os.path.expanduser(a)) else self.kernel.Print(os.getcwd())

  def line_print(self, a=''):
    self.kernel.Print(self.kernel._vars.get(a, f"{a} does not exist") if a else str(self.kernel._vars))

  def line_reset(self, a=''):
    self.kernel._vars = {
        "CC": "g++",
        "CFLAGS": "-std=c18 -march=native -O3 -fno-plt -fno-stack-protector -s -pipe",
        "CPPFLAGS": "-std=c++20 -march=native -O3 -fno-plt -fno-stack-protector -s -pipe",
        "LDFLAGS": "",
        "OFLAGS": "",
        "PFLAGS": "-tpng -darkmode",
      }

class GPPKernel(MetaKernel):
  implementation = 'Jupyter GPP Kernel'
  implementation_version = '0.1'
  language = 'c++'
  language_info = {
      'name': 'c++',
      'mimetype': 'text/x-cpp',
      'file_extension': '.cpp',
    }
  banner = implementation

  _cellcontents = ""

  def _exec_gpp(self, code):
    with tempfile.NamedTemporaryFile(dir=tempfile.gettempdir(), suffix=".out") as tmpfile:
      filename = tmpfile.name

    lang = "c" if self._vars['CC'] in ('gcc', 'clang') or "c" == self._cellcontents else "c++"
    flags = self._vars['CFLAGS' if 'c' == lang else 'CPPFLAGS']

    result = subprocess.run(
        f"{self._vars['CC']} {flags} -x{lang} {self._vars['LDFLAGS']} -o{filename} -&&{filename}",
        input=code.encode(),
        capture_output=True,
        shell=True,
      )

    os.remove(filename) if os.path.isfile(filename) else None

    return result

  def _exec_octave(self, code):
    return subprocess.run(
        f"octave {self._vars['OFLAGS']} -W",
        input=code.encode(),
        capture_output=True,
        shell=True,
      )

  def _exec_puml(self, code):
    return subprocess.run(
        f"plantuml {self._vars['PFLAGS']} -p",
        input=code.encode(),
        capture_output=True,
        shell=True,
      )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.register_magics(GPPMagics)
    self.call_magic('%reset')

  def do_execute_direct(self, code, silent=False):
    result = self._exec_octave(code) if 'octave' == self._cellcontents else self._exec_puml(code) if 'puml' == self._cellcontents else self._exec_gpp(code)
    self._cellcontents = ""

    self.kernel_resp = {
        'execution_count': self.execution_count,
        'payload': [],
        'status': 'error' if result.returncode else 'ok',
      }

    if result.returncode:
      output = result.stderr if result.stderr else result.stdout
      self.Error(output.decode())
    else:
      output = result.stdout

      if output.startswith(b'\x89PNG\r\n\x1a\n') or output.startswith(b'\xFF\xD8'):
        return Image(output)
      else:
        output = output.decode()

        return HTML(output) if re.search(r'<svg[^>]*>', output) else self.Write(output)

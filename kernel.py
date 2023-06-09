import cairosvg, os, re, subprocess, tempfile

from IPython.display import *
from metakernel import MetaKernel, Magic

class GPPMagics(Magic):
  def line_CC(self, a=''):
    self.kernel._vars["CC"] = a

  def line_BCFLAGS(self, a=''):
    self.line_BC()
    self.kernel._vars["BCFLAGS"] = a

  def line_CFLAGS(self, a=''):
    self.line_C()
    self.kernel._vars["CFLAGS"] = a

  def line_CPPFLAGS(self, a=''):
    self.kernel._cellcontents = ""
    self.kernel._vars["CPPFLAGS"] = a

  def line_LDFLAGS(self, a=''):
    self.kernel._vars["LDFLAGS"] = a

  def line_NFLAGS(self, a=''):
    self.line_NGSPICE()
    self.kernel._vars["NFLAGS"] = a

  def line_OFLAGS(self, a=''):
    self.line_OCTAVE()
    self.kernel._vars["OFLAGS"] = a

  def line_PFLAGS(self, a=''):
    self.line_PUML()
    self.kernel._vars["PFLAGS"] = a

  def line_BC(self, a=''):
    self.kernel._cellcontents = "bc"

  def line_C(self, a=''):
    self.kernel._cellcontents = "c"

  def line_NGSPICE(self, a=''):
    self.kernel._cellcontents = "ngspice"

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
        "CFLAGS": "-std=c18 -Wall -Wextra -march=native -O3 -fno-plt -fno-stack-protector -s -pipe",
        "CPPFLAGS": "-std=c++20 -Wall -Wextra -march=native -O3 -fno-plt -fno-stack-protector -s -pipe",
        "LDFLAGS": "",
        "BCFLAGS": "-l",
        "NFLAGS": "-b",
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

    lang = "c" if "c" == self._cellcontents or self._vars['CC'] in ('gcc', 'clang') else "c++"
    flags = self._vars['CFLAGS' if 'c' == lang else 'CPPFLAGS']

    result = subprocess.run(
        f"{self._vars['CC']} {flags} -x{lang} {self._vars['LDFLAGS']} -o{filename} -&&{filename}",
        input=code.encode(),
        capture_output=True,
        shell=True,
      )

    if os.path.isfile(filename): os.remove(filename)

    return result

  def _exec_bc(self, code):
    return subprocess.run(
        f"bc {self._vars['BCFLAGS']} -q <<< '{code}'",
        capture_output=True,
        shell=True,
      )

  def _exec_octave(self, code):
    return subprocess.run(
        f"octave {self._vars['OFLAGS']} -Wq",
        input=code.encode(),
        capture_output=True,
        shell=True,
      )

  def _exec_ngspice(self, code):
    return subprocess.run(
        f"ngspice {self._vars['NFLAGS']}",
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
    result = self._exec_bc(code) if 'bc' == self._cellcontents else self._exec_ngspice(code) if 'ngspice' == self._cellcontents else self._exec_octave(code) if 'octave' == self._cellcontents else self._exec_puml(code) if 'puml' == self._cellcontents else self._exec_gpp(code)
    self._cellcontents = ""

    self.kernel_resp = {
        'execution_count': self.execution_count,
        'payload': [],
        'status': 'error' if result.returncode else 'ok',
      }

    if output := result.stderr:
      self.Error(output.decode())

    if output := result.stdout:
      if output.startswith(b'\x89PNG\r\n\x1a\n') or output.startswith(b'\xFF\xD8') or output.startswith(b'\x47\x49\x46\x38\x37\x61') or output.startswith(b'\x47\x49\x46\x38\x39\x61'):
        return Image(output)
      else:
        output = output.decode()
        svg = re.search(r"(?s)(<\?xml.*?\?>)?.*?<svg[^>]*>.*?<\/svg>", output)

        return Image(cairosvg.svg2png(bytestring=svg.group(0))) if svg else self.Write(output)

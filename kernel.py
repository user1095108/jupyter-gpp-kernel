import os, re, subprocess, tempfile

from IPython.display import HTML, Image
from metakernel import MetaKernel, Magic

class GPPMagics(Magic):
  def line_CC(self, a=''):
    self.kernel._vars["CC"] = a if a else (self.kernel.Print(self.kernel._vars["CC"]) or self.kernel._vars["CC"])

  def line_CFLAGS(self, a=''):
    self.kernel._vars["CFLAGS"] = a if a else (self.kernel.Print(self.kernel._vars["CFLAGS"]) or self.kernel._vars["CFLAGS"])

  def line_PFLAGS(self, a=''):
    self.kernel._vars["PFLAGS"] = a if a else (self.kernel.Print(self.kernel._vars["PFLAGS"]) or self.kernel._vars["PFLAGS"])

  def line_cd(self, a=''):
    os.chdir(os.path.expanduser(a)) if a else self.kernel.Print(os.getcwd())

  def line_reset(self, a=''):
    self.kernel._vars = {
      "CC": "g++",
      "CFLAGS": "-std=c++20 -O3 -s -fno-stack-protector",
      "PFLAGS": "-tpng",
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

  def _exec_gpp(self, filename, code):
    return subprocess.run(
        f"{self._vars['CC']} {self._vars['CFLAGS']} -xc++ -o{filename} -&&{filename}",
        input=code.encode(),
        capture_output=True,
        shell=True,
      )

  def _exec_puml(self, filename, code):
    return subprocess.run(
        f"plantuml {self._vars['PFLAGS']} -p",
        input=code.encode(),
        capture_output=True,
        shell=True,
      )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.register_magics(GPPMagics)
    self.call_magic("%reset")

  def do_execute_direct(self, code, silent=False):
    with tempfile.NamedTemporaryFile(dir=tempfile.gettempdir(), suffix=".out") as tmpfile:
      tmpfilename = tmpfile.name

    result = self._exec_puml(tmpfilename, code) if code.lstrip().startswith("@start") else self._exec_gpp(tmpfilename, code)
    os.remove(tmpfilename) if os.path.isfile(tmpfilename) else None
    output = result.stderr if result.returncode else result.stdout

    self.kernel_resp = {
      'execution_count': self.execution_count,
      'payload': [],
      'status': "error" if result.returncode else 'ok',
    }

    if result.returncode:
      self.Error(output.decode())
    elif output.startswith(b'\x89PNG\r\n\x1a\n') or output.startswith(b'\xFF\xD8'):
      return Image(output)
    else:
      txt = output.decode()

      if re.search(r'<svg[^>]*>', txt):
        return HTML(txt)
      else:
        self.Write(txt)

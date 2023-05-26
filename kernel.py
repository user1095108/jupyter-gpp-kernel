import os, re, subprocess, tempfile

from IPython.display import HTML, Image
from metakernel import MetaKernel, Magic

class GPPMagics(Magic):
  def line_CC(self, args=''):
    self.kernel._vars["CC"] = args

  def line_CFLAGS(self, args=''):
    self.kernel._vars["CFLAGS"] = args

  def line_cd(self, args=''):
    if args:
      os.chdir(os.path.expanduser(args))
    else:
      self.kernel.Print(os.getcwd())

  def line_get(self, args=''):
    self.kernel.Print(self.kernel._vars.get(args, f"{args} does not exist") if args else str(self.kernel._vars))

  def line_reset(self, args=''):
    self.kernel._vars = {
      "CC": "g++",
      "CFLAGS": "-std=c++20 -O3 -s -fno-stack-protector"
    }

class GPPKernel(MetaKernel):
  _dir = tempfile.gettempdir()

  implementation = 'Jupyter GPP Kernel'
  implementation_version = '0.1'
  language = 'c++'
  language_info = {
    'name': 'c++',
    'mimetype': 'text/x-cpp',
    'file_extension': '.cpp'
  }
  banner = implementation

  def _exec_gpp(self, code):
    with tempfile.NamedTemporaryFile(dir=self._dir, suffix=".out") as tmpfile:
      filename = tmpfile.name

    return subprocess.run(
        f"{self._vars['CC']} {self._vars['CFLAGS']} -xc++ -o{filename} -&&{filename}",
        input=code.encode(),
        capture_output=True,
        cwd=self._dir,
        shell=True,
      )

  def _exec_puml(self, code):
    with tempfile.NamedTemporaryFile(dir=self._dir, suffix=".out") as tmpfile:
      filename = tmpfile.name

    return subprocess.run(
        "plantuml -tpng -p",
        input=code.encode(),
        capture_output=True,
        cwd=self._dir,
        shell=True,
      )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.register_magics(GPPMagics)
    self.call_magic("%reset")

  def do_execute_direct(self, code, silent=False):
    if code.lstrip().startswith("@start"):
      result = self._exec_puml(code)
    else:
      result = self._exec_gpp(code)

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

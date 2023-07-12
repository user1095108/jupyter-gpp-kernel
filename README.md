# jupyter-gpp-kernel
This is a basic Jupyter kernel for [bc](https://www.gnu.org/software/bc/), [c](https://gcc.gnu.org/), [c++](https://gcc.gnu.org/), [ngspice](https://sourceforge.net/projects/ngspice/), [Octave](https://en.wikipedia.org/wiki/Octave) and [PlantUML](https://plantuml.com/) notebooks. It can render [GIF](https://en.wikipedia.org/wiki/GIF), [JPEG](https://en.wikipedia.org/wiki/JPEG), [PNG](https://en.wikipedia.org/wiki/PNG) and [SVG](https://en.wikipedia.org/wiki/SVG) diagrams.
```
conda install -c conda-forge cairosvg
```
```
jupyter kernelspec install --user jupyter-gpp-kernel
export PYTHONPATH=~/.local/share/jupyter/kernels:$PYTHONPATH
```

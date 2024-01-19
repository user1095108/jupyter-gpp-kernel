# jupyter-gpp-kernel
This is a basic Jupyter kernel for [bc](https://www.gnu.org/software/bc/), [c](https://gcc.gnu.org/), [c++](https://gcc.gnu.org/), [ngspice](https://sourceforge.net/projects/ngspice/), [Octave](https://octave.org/) and [PlantUML](https://plantuml.com/) notebooks. It can render [PNG](https://en.wikipedia.org/wiki/PNG) and [SVG](https://en.wikipedia.org/wiki/SVG) diagrams.
```
conda install -c conda-forge cairosvg
conda install -c conda-forge metakernel
```
```
jupyter kernelspec install --user jupyter-gpp-kernel
export PYTHONPATH=~/.local/share/jupyter/kernels:$PYTHONPATH
```

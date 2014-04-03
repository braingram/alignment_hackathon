#!/usr/bin/env python
"""
Ummm fuck vtk, it silently fails to load 8-bit tifs
"""


import sys

import vtk

# input image filename
if len(sys.argv) > 1:
    fn = sys.argv[1]
else:
    fn = 'test2.tif'
if len(sys.argv) > 2:
    x = float(sys.argv[2])
else:
    x = 0.
if len(sys.argv) > 3:
    y = float(sys.argv[3])
else:
    y = 0.

# image affine transform
affine = [1., 0., 0., 1., 20., 20.]

# renderer bounds
h = 100
w = 100
ox = 0.
oy = 0.

# -- steps --
# make renderer (preferrably offscren & no-x)
renderer = vtk.vtkRenderer()

# load image


def read_file(fn):
    if '.tif' in fn.lower():
        reader = vtk.vtkTIFFReader()
        reader.SetFileName(fn)
        reader.Update()
        ext = reader.GetDataExtent()
        reader = vtk.vtkImageReader()
        reader.SetDataExtent(ext)
        reader.SetDataScalarTypeToUnsignedChar()
        reader.SetFileName(fn)
        reader.Update()
        return reader
    elif '.jpg' in fn.lower():
        reader = vtk.vtkJPEGReader()
        reader.SetFileName(fn)
        return reader

reader = read_file(fn)
# add actor
mapper = vtk.vtkImageMapper()
#mapper.SetInputConnection(reader.GetOutputPort())
mapper.SetInput(reader.GetOutput())
# colorlevel = sets center of range
# colorwindow = sets range
#mapper.SetColorWindow(200)
#mapper.SetColorLevel(-100)
mapper.SetColorWindow(255)
mapper.SetColorLevel(127.5)
#mapper.SetColorWindow(65535)
#mapper.SetColorLevel(0)
#mapper.RenderToRectangleOn()
actor = vtk.vtkActor2D()
actor.SetMapper(mapper)
#actor = vtk.vtkImageActor()
#actor.SetInput(reader.GetOutput())

# transform ? (do this on the image?)
#actor.SetWidth(10)
#actor.SetHeight(10)
actor.SetPosition((x, y))  # TODO affine

# render
renderer.AddActor2D(actor)
renderer.SetBackground(0.2, 0.3, 0.4)

# return as string
# TODO

# display (for debugging)
interactor = vtk.vtkRenderWindowInteractor()
style = vtk.vtkInteractorStyleImage()
interactor.SetInteractorStyle(style)
window = vtk.vtkRenderWindow()
window.SetSize(800, 800)
window.AddRenderer(renderer)
interactor.SetRenderWindow(window)
window.Render()
interactor.Start()

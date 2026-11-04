#pragma once

namespace drake {
namespace internal {

/* Registers VTK's OpenGL2 object factory, so that VTK's abstract rendering
classes (e.g., vtkRenderer, vtkPolyDataMapper) instantiate their OpenGL
implementations. When the factory is not registered, VTK silently instantiates
the (possibly no-op) base class instead.

There are some VTK operations that depend on this, beyond the obvious
RenderEngineVtk; e.g., parsing glTF files (VTK parses glTF files directly into
OpenGL constructs). Any code that needs it must call this function prior to
creating the relevant VTK objects.

This function is idempotent and thread-safe. (We use an explicit call instead
of VTK_MODULE_INIT, because Drake forbids global constructors.) */
void VtkOpenGlInit();

}  // namespace internal
}  // namespace drake

// To ease build system upkeep, we annotate VTK includes with their deps.
#include "drake/tools/workspace/vtk_internal/vtk_opengl_init.h"

#include <vtkAutoInit.h>  // vtkCommonCore

VTK_AUTOINIT_DECLARE(vtkRenderingOpenGL2)

namespace drake {
namespace internal {

void VtkOpenGlInit() {
  // A function-local static runs the registration exactly once (and is
  // thread-safe). Using a trivially-destructible bool means we don't need any
  // static destructor.
  [[maybe_unused]] static const bool done = []() {
    vtkRenderingOpenGL2_AutoInit_Construct();
    return true;
  }();
}

}  // namespace internal
}  // namespace drake

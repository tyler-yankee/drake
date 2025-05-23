#pragma once

#include "drake/common/drake_copyable.h"
#include "drake/common/eigen_types.h"
#include "drake/systems/framework/leaf_system.h"

namespace drake {
namespace systems {

/// An element-wise hard saturation block with inputs signal `u`,
/// saturation values @f$ u_{min} @f$ and/or @f$ u_{max} @f$, and output
/// `y` respectively as in:
///
///   @f[ y = u, u_{min} < u < u_{max} @f]
///   @f[ y = u_{min}, u \le u_{min} @f]
///   @f[ y = u_{max}, u \ge u_{max}  @f]
///
/// The input to this system directly feeds through to its output.
///
/// Note that @f$ u_{min} @f$, and @f$ u_{max} @f$, and @f$ u @f$ are all
/// vectors of same dimension, and the following condition holds elementwise in
/// runtime.
///
///   @f[ u_{min} <=  u_{max} @f]
///
/// The quantities @f$ u_{min} @f$, and @f$ u_{max} @f$ can be supplied as
/// inputs in separate ports or be initialised as constants using the
/// appropriate constructor by passing their default value. If these quantities
/// are not defined as constants but they are not connected to appropriate
/// sources, their values are taken by default to be
/// @f$ u_{min} = -\infty @f$, and  @f$ u_{max} = \infty @f$ respectively.
/// In this "variable" configuration, at least one of the input ports must be
/// connected.
///
/// @system
/// name: Saturation
/// input_ports:
/// - u0
/// - <span style="color:gray">u1</span>
/// - <span style="color:gray">u2</span>
/// output_ports:
/// - y0
/// @endsystem
///
/// Ports show in <span style="color:gray">gray</span> may be absent, depending
/// on how the system is constructed.
///
/// @tparam_default_scalar
/// @ingroup primitive_systems
template <typename T>
class Saturation final : public LeafSystem<T> {
 public:
  DRAKE_NO_COPY_NO_MOVE_NO_ASSIGN(Saturation);

  /// Constructs a variable %Saturation system where the upper and lower values
  /// are represented by vectors of identical size and can be supplied via the
  /// max_value_port and min_value_port respectively.
  ///
  /// @system
  /// name: Saturation
  /// input_ports:
  /// - u0
  /// - u1
  /// - u2
  /// output_ports:
  /// - y0
  /// @endsystem
  ///
  /// Port `u1` is the source of @f$ u_{max} @f$; port `u2` is the source of
  /// @f$ u_{min} @f$.
  ///
  /// @param[in] input_size sets size of the input and output ports.
  ///
  /// Please consult this class's description for the requirements of
  /// @p u_min and @p u_max to be supplied via the corresponding ports.
  explicit Saturation(int input_size);

  /// Constructs a constant %Saturation system where the upper and lower
  /// values are represented by vectors of identical size supplied via this
  /// constructor.
  ///
  /// @system
  /// name: Saturation
  /// input_ports:
  /// - u0
  /// output_ports:
  /// - y0
  /// @endsystem
  ///
  /// @param[in] min_value the lower (vector) limit to the saturation.
  /// @param[in] max_value the upper (vector) limit to the saturation.
  ///
  /// Please consult this class's description for the requirements of
  /// @p min_value and @p max_value.
  Saturation(const VectorX<T>& min_value, const VectorX<T>& max_value);

  /// Scalar-converting copy constructor.  See @ref system_scalar_conversion.
  template <typename U>
  explicit Saturation(const Saturation<U>&);

  /// Returns the input port.
  const InputPort<T>& get_input_port() const {
    return System<T>::get_input_port(input_port_index_);
  }

  /// Returns the min value port.
  const InputPort<T>& get_min_value_port() const {
    DRAKE_THROW_UNLESS(min_max_ports_enabled_);
    return System<T>::get_input_port(min_value_port_index_);
  }

  /// Returns the max value port.
  const InputPort<T>& get_max_value_port() const {
    DRAKE_THROW_UNLESS(min_max_ports_enabled_);
    return System<T>::get_input_port(max_value_port_index_);
  }

  /// Returns the size.
  int get_size() const { return input_size_; }
  // TODO(naveenoid) : Add a witness function for capturing events when
  // saturation limits are reached.

 private:
  template <typename>
  friend class Saturation;

  // Constructors' implementation.
  Saturation(bool min_max_ports_enabled, int input_size,
             const VectorX<T>& min_value, const VectorX<T>& max_value);

  void CalcSaturatedOutput(const Context<T>& context,
                           BasicVector<T>* output_vector) const;

  int input_port_index_{};
  int min_value_port_index_{};
  int max_value_port_index_{};
  const bool min_max_ports_enabled_{false};
  const int input_size_{};
  const VectorX<T> min_value_;
  const VectorX<T> max_value_;
};

}  // namespace systems
}  // namespace drake

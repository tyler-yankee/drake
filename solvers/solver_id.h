#pragma once

#include <functional>
#include <string>

#include "drake/common/drake_copyable.h"
#include "drake/common/fmt.h"
#include "drake/common/hash.h"
#include "drake/common/reset_after_move.h"

namespace drake {
namespace solvers {

/** Identifies a SolverInterface implementation.

A moved-from instance is guaranteed to be empty and will not compare equal to
any non-empty ID. */
class SolverId {
 public:
  DRAKE_DEFAULT_COPY_AND_MOVE_AND_ASSIGN(SolverId);
  ~SolverId() = default;

  /** Constructs a specific, known solver type. Internally, a hidden integer is
  allocated and assigned to this instance; all instances that share an integer
  (including copies of this instance) are considered equal. The solver names are
  not enforced to be unique, though we recommend that they remain so in
  practice.

  For best performance, choose a name that is 15 characters or less, so that it
  fits within the libstdc++ "small string" optimization ("SSO"). */
  explicit SolverId(std::string name);

  const std::string& name() const { return name_; }

  /** Implements the @ref hash_append concept. */
  template <class HashAlgorithm>
  // NOLINTNEXTLINE(runtime/references) Per hash_append convention.
  friend void hash_append(HashAlgorithm& hasher,
                          const SolverId& item) noexcept {
    using drake::hash_append;
    hash_append(hasher, int{item.id_});
    // We do not send the name_ to the hasher, because the id_ is already
    // unique across all instances.
  }

 private:
  friend bool operator==(const SolverId&, const SolverId&);
  friend bool operator!=(const SolverId&, const SolverId&);
  friend struct std::less<SolverId>;

  reset_after_move<int> id_;
  std::string name_;
};

bool operator==(const SolverId&, const SolverId&);
bool operator!=(const SolverId&, const SolverId&);

std::string to_string(const SolverId&);

}  // namespace solvers
}  // namespace drake

namespace std {
/* Provides std::less<drake::solvers::SolverId>. */
template <>
struct less<drake::solvers::SolverId> {
  bool operator()(const drake::solvers::SolverId& lhs,
                  const drake::solvers::SolverId& rhs) const {
    return lhs.id_ < rhs.id_;
  }
};

#ifdef _LIBCPP_VERSION
#if __has_include(<__type_traits/make_transparent.h>)
// Recent versions of libc++ substitute std::less<> for std::less<T> when
// searching a std::set or std::map, which would bypass our specialization
// above. Opt out of that substitution.
// https://issues.fuchsia.dev/issues/447427729
// https://github.com/llvm/llvm-project/pull/157866
template <>
struct __make_transparent<drake::solvers::SolverId,
                          less<drake::solvers::SolverId>> {
  using type = less<drake::solvers::SolverId>;
};
#endif  // make_transparent.h
#endif  // _LIBCPP_VERSION

/* Provides std::hash<drake::solvers::SolverId>. */
template <>
struct hash<drake::solvers::SolverId> : public drake::DefaultHash {};
}  // namespace std

DRAKE_FORMATTER_AS(, drake::solvers, SolverId, x, drake::solvers::to_string(x))

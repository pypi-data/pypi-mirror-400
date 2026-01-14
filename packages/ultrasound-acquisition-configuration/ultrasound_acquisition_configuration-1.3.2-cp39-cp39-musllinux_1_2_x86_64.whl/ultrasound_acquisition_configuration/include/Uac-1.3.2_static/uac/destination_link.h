#pragma once

#include <algorithm>
#include <memory>
#include <optional>
#include <utility>
#include <vector>

#include <uac/trigger.h>

namespace uac {

struct IGroup;  // IWYU pragma: keep

struct DestinationLink {
  bool operator==(const DestinationLink& other) const {
    std::vector<std::pair<const void*, const void*>> already_compared_obj;
    return secureComparison(other, already_compared_obj);
  }

  bool operator!=(const DestinationLink& other) const { return !operator==(other); }

  bool secureComparison(
      const DestinationLink& other,
      std::vector<std::pair<const void*, const void*>>& already_compared_obj) const;

  std::optional<TriggerIn> trigger;

  std::weak_ptr<IGroup> destination;
};

}  // namespace uac

// NOLINTNEXTLINE(misc-header-include-cycle)
#include <uac/igroup.h>  // IWYU pragma: keep

namespace uac {

// NOLINTNEXTLINE(misc-no-recursion)
inline bool DestinationLink::secureComparison(
    const DestinationLink& other,
    std::vector<std::pair<const void*, const void*>>& already_compared_obj) const {
  auto lhs_lock = destination.lock();
  auto rhs_lock = other.destination.lock();
  const std::pair<const void*, const void*> comparison_pair(static_cast<const void*>(this),
                                                            static_cast<const void*>(&other));
  const std::pair<const void*, const void*> comparison_pair_miror(static_cast<const void*>(&other),
                                                                  static_cast<const void*>(this));

  const bool eq_res = trigger == other.trigger;

  if (std::find_if(already_compared_obj.begin(), already_compared_obj.end(),
                   [&comparison_pair, &comparison_pair_miror](const auto& it) {
                     return it == comparison_pair || it == comparison_pair_miror;
                   }) == already_compared_obj.end()) {
    already_compared_obj.push_back(comparison_pair);
    return eq_res &&
           // NOLINTNEXTLINE(misc-no-recursion)
           (((lhs_lock && rhs_lock) ? (lhs_lock->secureComparison(*rhs_lock, already_compared_obj))
                                    : (!!lhs_lock == !!rhs_lock)));
  }
  return eq_res;
}

}  // namespace uac

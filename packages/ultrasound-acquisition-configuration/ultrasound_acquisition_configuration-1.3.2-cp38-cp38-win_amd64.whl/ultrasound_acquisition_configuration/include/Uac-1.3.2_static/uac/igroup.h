#pragma once

#include <algorithm>
#include <cstdint>
#include <memory>
#include <optional>
#include <utility>
#include <vector>

#include <urx/detail/double_nan.h>

#include <uac/hw_config.h>
#include <uac/trigger.h>

namespace uac {

struct DestinationLink;  // IWYU pragma: keep

struct IGroup {
  virtual bool operator==(const IGroup& other) const {
    std::vector<std::pair<const void*, const void*>> already_compared_obj;
    return secureComparison(other, already_compared_obj);
  }

  virtual ~IGroup() = 0;

  virtual bool operator!=(const IGroup& other) const { return !operator==(other); }

  virtual bool secureComparison(
      const IGroup& other,
      std::vector<std::pair<const void*, const void*>>& already_compared_obj) const;

  urx::DoubleNan time_offset{0};

  std::optional<TriggerIn> trigger_in;

  std::optional<TriggerOut> trigger_out;

  uint32_t repetition_count = 0;

  std::vector<DestinationLink> destinations;

  urx::DoubleNan period;

  HwConfig hw_config;
};

}  // namespace uac

// NOLINTNEXTLINE(misc-header-include-cycle)
#include <uac/destination_link.h>  // IWYU pragma: keep

namespace uac {

// NOLINTNEXTLINE(misc-no-recursion)
inline bool IGroup::secureComparison(
    const IGroup& other,
    std::vector<std::pair<const void*, const void*>>& already_compared_obj) const {
  const std::pair<const void*, const void*> comparison_pair(static_cast<const void*>(this),
                                                            static_cast<const void*>(&other));
  const std::pair<const void*, const void*> comparison_pair_miror(static_cast<const void*>(&other),
                                                                  static_cast<const void*>(this));

  const bool eq_res = time_offset == other.time_offset && trigger_in == other.trigger_in &&
                      trigger_out == other.trigger_out &&
                      repetition_count == other.repetition_count && period == other.period &&
                      hw_config == other.hw_config;
  if (std::find_if(already_compared_obj.begin(), already_compared_obj.end(),
                   [&comparison_pair, &comparison_pair_miror](const auto& it) {
                     return it == comparison_pair || it == comparison_pair_miror;
                   }) == already_compared_obj.end()) {
    already_compared_obj.push_back(comparison_pair);
    return eq_res && (std::equal(destinations.cbegin(), destinations.cend(),
                                 other.destinations.cbegin(), other.destinations.cend(),
                                 // NOLINTNEXTLINE(misc-no-recursion)
                                 [&already_compared_obj](const DestinationLink& dl1,
                                                         const DestinationLink& dl2) {
                                   // NOLINTNEXTLINE(misc-no-recursion)
                                   return dl1.secureComparison(dl2, already_compared_obj);
                                 }));
  }
  return eq_res;
}

inline IGroup::~IGroup() = default;

}  // namespace uac

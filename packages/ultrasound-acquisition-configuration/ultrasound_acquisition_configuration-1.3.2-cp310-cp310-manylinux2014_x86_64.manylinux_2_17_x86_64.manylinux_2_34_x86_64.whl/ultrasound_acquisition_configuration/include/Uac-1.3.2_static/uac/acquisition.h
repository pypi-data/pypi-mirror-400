#pragma once

#include <algorithm>
#include <memory>
#include <optional>
#include <utility>
#include <vector>

#include <urx/acquisition.h>
#include <urx/detail/compare.h>
#include <urx/detail/double_nan.h>

#include <uac/excitation.h>
#include <uac/group.h>
#include <uac/hw_config.h>
#include <uac/igroup.h>
#include <uac/super_group.h>
#include <uac/trigger.h>

namespace uac {

struct Acquisition : urx::detail::AcquisitionBase<Excitation, Group> {
  bool operator==(const Acquisition& other) const {
    return urx::detail::AcquisitionBase<Excitation, Group>::operator==(other) &&
           urx::valueComparison(initial_group, other.initial_group) &&
           urx::valueComparison(super_groups, other.super_groups) &&
           time_offset == other.time_offset && trigger_in == other.trigger_in &&
           trigger_out == other.trigger_out && hw_config == other.hw_config;
  }

  bool operator!=(const Acquisition& other) const { return !operator==(other); }

  std::vector<std::shared_ptr<SuperGroup>> super_groups;

  std::weak_ptr<IGroup> initial_group;

  urx::DoubleNan time_offset{0};

  std::optional<TriggerIn> trigger_in;

  std::optional<TriggerOut> trigger_out;

  HwConfig hw_config;
};

}  // namespace uac

#pragma once

#include <algorithm>
#include <optional>

#include <urx/detail/double_nan.h>
#include <urx/event.h>

#include <uac/hw_config.h>
#include <uac/receive_setup.h>
#include <uac/transmit_setup.h>
#include <uac/trigger.h>

namespace uac {

struct Event : urx::detail::Event<TransmitSetup, ReceiveSetup> {
  bool operator==(const Event& other) const {
    return urx::detail::Event<TransmitSetup, ReceiveSetup>::operator==(other) &&
           time_offset == other.time_offset && trigger_in == other.trigger_in &&
           trigger_out == other.trigger_out && hw_config == other.hw_config;
  }

  bool operator!=(const Event& other) const { return !operator==(other); }

  urx::DoubleNan time_offset{0};

  std::optional<TriggerIn> trigger_in;

  std::optional<TriggerOut> trigger_out;

  HwConfig hw_config;
};

}  // namespace uac

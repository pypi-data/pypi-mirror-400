#pragma once

#include <string>
#include <utility>

#include <urx/detail/double_nan.h>

#include <uac/enums.h>

namespace uac {

struct TriggerIn {
  bool operator==(const TriggerIn& other) const {
    return channel == other.channel && edge == other.edge;
  }

  bool operator!=(const TriggerIn& other) const { return !operator==(other); }

  std::string channel;
  Edge edge = Edge::UNDEFINED;
};

struct TriggerOut {
  bool operator==(const TriggerOut& other) const {
    return channel == other.channel && time_offset == other.time_offset &&
           pulse_duration == other.pulse_duration && polarity == other.polarity;
  }

  bool operator!=(const TriggerOut& other) const { return !operator==(other); }

  std::string channel;
  urx::DoubleNan time_offset{0};
  urx::DoubleNan pulse_duration;
  Polarity polarity = Polarity::UNDEFINED;
};

}  // namespace uac

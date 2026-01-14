#pragma once

#include <urx/receive_setup.h>

#include <uac/hw_config.h>

namespace uac {

struct ReceiveSetup : urx::ReceiveSetup {
  bool operator==(const ReceiveSetup& other) const {
    return urx::ReceiveSetup::operator==(other) && hw_config == other.hw_config;
  }

  bool operator!=(const ReceiveSetup& other) const { return !operator==(other); }

  HwConfig hw_config;
};

}  // namespace uac

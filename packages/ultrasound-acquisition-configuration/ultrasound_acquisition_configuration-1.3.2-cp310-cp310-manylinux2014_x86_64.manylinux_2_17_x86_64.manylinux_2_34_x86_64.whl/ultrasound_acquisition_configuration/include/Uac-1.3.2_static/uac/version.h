#pragma once

#include <cstddef>

#include <urx/version.h>

#include <uac/uac.h>

namespace uac {

struct Version : urx::Version {
  Version() : urx::Version{UAC_VERSION_MAJOR, UAC_VERSION_MINOR, UAC_VERSION_PATCH} {}
  Version(uint16_t major_val, uint16_t minor_val, uint16_t patch_val)
      : urx::Version{major_val, minor_val, patch_val} {}
};

}  // namespace uac

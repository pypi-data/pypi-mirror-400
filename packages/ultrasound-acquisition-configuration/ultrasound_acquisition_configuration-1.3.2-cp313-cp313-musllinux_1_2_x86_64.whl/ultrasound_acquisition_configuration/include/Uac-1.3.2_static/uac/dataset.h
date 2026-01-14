#pragma once

#include <algorithm>

#include <urx/dataset.h>

#include <uac/acquisition.h>
#include <uac/version.h>

namespace uac {
using Dataset = urx::detail::Dataset<Acquisition, Version>;
}  // namespace uac

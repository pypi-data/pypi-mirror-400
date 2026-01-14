#pragma once

#include <urx/enums.h>

namespace uac {
using SamplingType = urx::SamplingType;
using DataType = urx::DataType;
using ProbeType = urx::ProbeType;
using WaveType = urx::WaveType;

enum class Edge { RISING = 0, FALLING = 1, HIGH = 2, LOW = 3, UNDEFINED = -1 };

enum class Polarity { POSITIVE = 0, NEGATIVE = 1, UNDEFINED = -1 };
}  // namespace uac

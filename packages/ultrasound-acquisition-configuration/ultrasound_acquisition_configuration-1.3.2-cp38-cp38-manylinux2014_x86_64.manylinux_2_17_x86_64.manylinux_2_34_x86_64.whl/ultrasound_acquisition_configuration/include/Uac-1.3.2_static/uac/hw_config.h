#pragma once

#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>
#include <unordered_map>
#include <utility>
#include <variant>
#include <vector>

namespace uac {

struct HwConfig {
  template <class... Args>
  struct VariantType {
    using TypeAndVector = std::variant<Args..., std::vector<Args>...>;
  };

// Recursive complete struct in std::variant need at least gcc-12 / clang-15.
#if defined(__GNUC__) && !defined(__clang__) && !defined(__INTEL_COMPILER)
  static_assert(__GNUC__ >= 12);
#endif
#ifdef __clang__
  static_assert(__clang_major__ >= 15);
#endif
  using VecDataTypeVariant =
      VariantType<int8_t, int16_t, int32_t, int64_t, uint8_t, uint16_t, uint32_t, uint64_t, float,
                  double, std::string, HwConfig>::TypeAndVector;

  bool operator==(const HwConfig& other) const { return values == other.values; }

  bool operator!=(const HwConfig& other) const { return !operator==(other); }

  using Values = std::unordered_map<std::string, VecDataTypeVariant>;

  Values values;
};

}  // namespace uac
#pragma once

#include <algorithm>
#include <memory>
#include <utility>
#include <vector>

#include <urx/detail/double_nan.h>
#include <urx/enums.h>
#include <urx/vector.h>

namespace urx {

struct Wave {
  bool operator==(const Wave& other) const {
    return type == other.type && time_zero == other.time_zero &&
           time_zero_reference_point == other.time_zero_reference_point &&
           parameters == other.parameters;
  }

  bool operator!=(const Wave& other) const { return !operator==(other); }

  WaveType type = WaveType::UNDEFINED;

  DoubleNan time_zero;

  Vector3D<double> time_zero_reference_point;

  std::vector<double> parameters;
};

}  // namespace urx

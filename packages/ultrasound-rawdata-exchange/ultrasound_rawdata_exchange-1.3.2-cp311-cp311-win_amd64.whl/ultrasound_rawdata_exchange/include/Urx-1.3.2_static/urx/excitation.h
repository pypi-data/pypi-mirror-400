#pragma once

#include <algorithm>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include <urx/detail/double_nan.h>

namespace urx {

struct Excitation {
  bool operator==(const Excitation& other) const {
    return pulse_shape == other.pulse_shape && transmit_frequency == other.transmit_frequency &&
           sampling_frequency == other.sampling_frequency && waveform == other.waveform;
  }

  bool operator!=(const Excitation& other) const { return !operator==(other); }

  std::string pulse_shape;

  DoubleNan transmit_frequency;
  DoubleNan sampling_frequency;

  std::vector<double> waveform;
};

}  // namespace urx

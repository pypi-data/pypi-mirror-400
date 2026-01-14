#pragma once

#include <algorithm>
#include <cstdint>
#include <memory>
#include <utility>
#include <vector>

#include <urx/detail/compare.h>
#include <urx/detail/double_nan.h>
#include <urx/probe.h>
#include <urx/transform.h>

namespace urx {

struct ReceiveSetup {
  bool operator==(const ReceiveSetup& other) const {
    return valueComparison(probe, other.probe) && probe_transform == other.probe_transform &&
           sampling_frequency == other.sampling_frequency &&
           number_samples == other.number_samples && active_elements == other.active_elements &&
           tgc_profile == other.tgc_profile &&
           tgc_sampling_frequency == other.tgc_sampling_frequency &&
           modulation_frequency == other.modulation_frequency && time_offset == other.time_offset;
  }

  bool operator!=(const ReceiveSetup& other) const { return !operator==(other); }

  std::weak_ptr<Probe> probe;

  Transform probe_transform;

  DoubleNan sampling_frequency;

  uint32_t number_samples = 0;

  std::vector<std::vector<uint32_t>> active_elements;

  std::vector<double> tgc_profile;
  DoubleNan tgc_sampling_frequency;

  DoubleNan modulation_frequency;
  DoubleNan time_offset{0};
};

}  // namespace urx

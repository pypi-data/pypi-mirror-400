#pragma once

#include <algorithm>
#include <cstdint>
#include <memory>
#include <utility>
#include <vector>

#include <urx/detail/compare.h>
#include <urx/detail/double_nan.h>
#include <urx/excitation.h>
#include <urx/probe.h>
#include <urx/transform.h>
#include <urx/wave.h>

namespace urx {

namespace detail {
template <class Excitation>
struct TransmitSetup {
  bool operator==(const TransmitSetup& other) const {
    return valueComparison(probe, other.probe) && wave == other.wave &&
           probe_transform == other.probe_transform && time_offset == other.time_offset &&
           active_elements == other.active_elements &&
           valueComparison(excitations, other.excitations) && delays == other.delays;
  }

  bool operator!=(const TransmitSetup& other) const { return !operator==(other); }

  std::weak_ptr<Probe> probe;
  Wave wave;

  std::vector<std::vector<uint32_t>> active_elements;
  std::vector<std::weak_ptr<Excitation>> excitations;
  std::vector<double> delays;

  Transform probe_transform;

  DoubleNan time_offset{0};
};
}  // namespace detail
using TransmitSetup = detail::TransmitSetup<Excitation>;

}  // namespace urx

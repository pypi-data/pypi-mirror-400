#pragma once

#include <algorithm>
#include <string>
#include <vector>

#include <urx/acquisition.h>
#include <urx/version.h>

namespace urx {

// Root class. See wiki for documentation.

namespace detail {
template <class Acquisition, class Version>
struct Dataset {
  bool operator==(const Dataset& other) const {
    return version == other.version && acquisition == other.acquisition;
  }

  bool operator!=(const Dataset& other) const { return !operator==(other); }

  Acquisition acquisition;

  Version version;
};
}  // namespace detail
using Dataset = detail::Dataset<Acquisition, Version>;

}  // namespace urx

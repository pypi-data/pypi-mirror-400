#pragma once

#include <cstddef>

#include <urx/urx.h>

namespace urx {

struct Version {
  bool operator==(const Version& other) const {
    return major == other.major && minor == other.minor && patch == other.patch;
  }

  bool operator!=(const Version& other) const { return !operator==(other); }

  uint16_t major = URX_VERSION_MAJOR;
  uint16_t minor = URX_VERSION_MINOR;
  uint16_t patch = URX_VERSION_PATCH;
};

}  // namespace urx

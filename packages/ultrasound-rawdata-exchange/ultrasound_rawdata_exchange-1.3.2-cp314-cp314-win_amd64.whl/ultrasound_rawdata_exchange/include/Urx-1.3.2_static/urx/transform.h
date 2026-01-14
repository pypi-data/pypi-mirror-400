#pragma once

#include <urx/vector.h>

namespace urx {

struct Transform {
  bool operator==(const Transform& other) const {
    return rotation == other.rotation && translation == other.translation;
  }

  bool operator!=(const Transform& other) const { return !operator==(other); }

  Vector3D<double> rotation;
  Vector3D<double> translation;
};

}  // namespace urx

#pragma once

#include <algorithm>
#include <memory>
#include <utility>
#include <vector>

#include <urx/vector.h>

namespace urx {

struct ElementGeometry {
  bool operator==(const ElementGeometry& other) const { return perimeter == other.perimeter; }
  bool operator!=(const ElementGeometry& other) const { return !(*this == other); }

  std::vector<Vector3D<double>> perimeter;
};

}  // namespace urx

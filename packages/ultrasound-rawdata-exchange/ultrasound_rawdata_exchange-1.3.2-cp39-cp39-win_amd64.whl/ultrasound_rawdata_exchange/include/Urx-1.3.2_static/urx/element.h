#pragma once

#include <memory>

#include <urx/detail/compare.h>
#include <urx/element_geometry.h>
#include <urx/impulse_response.h>
#include <urx/transform.h>

namespace urx {

struct Element {
  bool operator==(const Element& other) const {
    return transform == other.transform &&
           valueComparison(element_geometry, other.element_geometry) &&
           valueComparison(impulse_response, other.impulse_response);
  }

  bool operator!=(const Element& other) const { return !operator==(other); }

  Transform transform;

  std::weak_ptr<ElementGeometry> element_geometry;
  std::weak_ptr<ImpulseResponse> impulse_response;
};

}  // namespace urx

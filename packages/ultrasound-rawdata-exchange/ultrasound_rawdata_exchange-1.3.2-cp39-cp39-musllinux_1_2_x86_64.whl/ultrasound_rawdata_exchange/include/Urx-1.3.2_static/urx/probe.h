#pragma once

#include <algorithm>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include <urx/detail/compare.h>
#include <urx/element.h>
#include <urx/element_geometry.h>
#include <urx/enums.h>
#include <urx/impulse_response.h>
#include <urx/transform.h>

namespace urx {

struct Probe {
  bool operator==(const Probe& other) const {
    return description == other.description && type == other.type && transform == other.transform &&
           valueComparison(element_geometries, other.element_geometries) &&
           valueComparison(impulse_responses, other.impulse_responses) &&
           elements == other.elements;
  }

  bool operator!=(const Probe& other) const { return !operator==(other); }

  std::string description;

  ProbeType type = ProbeType::UNDEFINED;

  Transform transform;

  std::vector<std::shared_ptr<ElementGeometry>> element_geometries;
  std::vector<std::shared_ptr<ImpulseResponse>> impulse_responses;

  std::vector<Element> elements;
};

}  // namespace urx

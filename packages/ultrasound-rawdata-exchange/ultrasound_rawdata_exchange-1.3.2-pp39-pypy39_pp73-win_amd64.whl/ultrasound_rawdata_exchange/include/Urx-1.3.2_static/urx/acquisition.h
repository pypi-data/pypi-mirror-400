#pragma once

#include <algorithm>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include <urx/detail/compare.h>
#include <urx/detail/double_nan.h>
#include <urx/excitation.h>
#include <urx/group.h>
#include <urx/group_data.h>
#include <urx/probe.h>

namespace urx {

namespace detail {
template <class Excitation, class Group>
struct AcquisitionBase {
  bool operator==(const AcquisitionBase& other) const {
    return authors == other.authors && description == other.description &&
           local_time == other.local_time && country_code == other.country_code &&
           system == other.system && timestamp == other.timestamp &&
           valueComparison(probes, other.probes) &&
           valueComparison(excitations, other.excitations) && valueComparison(groups, other.groups);
  }

  bool operator!=(const AcquisitionBase& other) const { return !operator==(other); }

  std::string authors;
  std::string description;
  std::string local_time;
  std::string country_code;
  std::string system;

  DoubleNan timestamp;

  std::vector<std::shared_ptr<Probe>> probes;
  std::vector<std::shared_ptr<Excitation>> excitations;
  std::vector<std::shared_ptr<Group>> groups;
};

template <class Excitation, class Group>
struct Acquisition : public AcquisitionBase<Excitation, Group> {
  bool operator==(const Acquisition& other) const {
    return AcquisitionBase<Excitation, Group>::operator==(other) &&
           groups_data == other.groups_data;
  }

  bool operator!=(const Acquisition& other) const { return !operator==(other); }

  std::vector<GroupData> groups_data;
};

}  // namespace detail

using Acquisition = detail::Acquisition<Excitation, Group>;

}  // namespace urx

#pragma once

#include <algorithm>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include <urx/detail/compare.h>
#include <urx/detail/double_nan.h>
#include <urx/detail/raw_data.h>
#include <urx/group.h>

namespace urx {

struct GroupData {
  bool operator==(const GroupData& other) const {
    return valueComparison(group, other.group) && valueComparison(raw_data, other.raw_data) &&
           group_timestamp == other.group_timestamp &&
           sequence_timestamps == other.sequence_timestamps &&
           event_timestamps == other.event_timestamps;
  }

  bool operator!=(const GroupData& other) const { return !operator==(other); }

  std::weak_ptr<Group> group;
  std::shared_ptr<RawData> raw_data = std::make_shared<RawDataVector<float>>(std::vector<float>());

  DoubleNan group_timestamp;

  std::vector<double> sequence_timestamps;
  std::vector<std::vector<double>> event_timestamps;
};

}  // namespace urx

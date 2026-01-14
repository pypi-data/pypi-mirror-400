#pragma once

namespace urx {
enum class ProbeType {
  LINEAR = 0,
  CURVILINEAR = 1,
  RCA = 2,
  MATRIX = 3,
  SPARSE = 4,
  UNDEFINED = -1
};

enum class WaveType {
  CONVERGING_WAVE = 0,
  DIVERGING_WAVE = 1,
  PLANE_WAVE = 2,
  CYLINDRICAL_WAVE = 3,
  UNDEFINED = -1
};

enum class SamplingType { RF = 0, IQ = 1, UNDEFINED = -1 };

enum class DataType { INT16 = 0, INT32 = 1, FLOAT = 2, DOUBLE = 3, UNDEFINED = -1 };
}  // namespace urx

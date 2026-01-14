#pragma once

#include <cmath>
#include <functional>
#include <limits>
#include <type_traits>

namespace urx {

struct DoubleNan {
  static constexpr double URX_NAN = std::numeric_limits<double>::quiet_NaN();

  double value = URX_NAN;

  DoubleNan() = default;
  template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
  explicit DoubleNan(T v) : value(static_cast<double>(v)) {}
  DoubleNan(const DoubleNan&) = default;

  bool operator<(const DoubleNan& other) const { return value < other.value; }

  bool operator<=(const DoubleNan& other) const { return value <= other.value; }

  bool operator>(const DoubleNan& other) const { return value > other.value; }

  bool operator>=(const DoubleNan& other) const { return value >= other.value; }

  bool operator==(const DoubleNan& other) const {
    if (std::isnan(value) && std::isnan(other.value)) {
      return true;
    }
    return std::equal_to<>()(value, other.value);
  }

  bool operator!=(const DoubleNan& other) const { return !operator==(other); }

  // NOLINTNEXTLINE(google-explicit-constructor,hicpp-explicit-conversions)
  operator double() const { return value; }

  template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
  DoubleNan& operator=(T n) {
    value = static_cast<double>(n);
    return *this;
  }
  template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
  DoubleNan operator+(T n) const {
    return DoubleNan(value + n);
  }
  template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
  DoubleNan operator-(T n) const {
    return DoubleNan(value - n);
  }
  template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
  DoubleNan operator/(T n) const {
    return DoubleNan(value / n);
  }
  template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
  DoubleNan operator*(T n) const {
    return DoubleNan(value * n);
  }
  DoubleNan& operator=(const DoubleNan& n) = default;
  DoubleNan& operator+=(const DoubleNan& n) {
    value += n.value;
    return *this;
  }
  DoubleNan& operator-=(const DoubleNan& n) {
    value -= n.value;
    return *this;
  }
  DoubleNan& operator/=(const DoubleNan& n) {
    value /= n.value;
    return *this;
  }
  DoubleNan& operator*=(const DoubleNan& n) {
    value *= n.value;
    return *this;
  }
  template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
  DoubleNan& operator+=(T n) {
    value += n;
    return *this;
  }
  template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
  DoubleNan& operator-=(T n) {
    value -= n;
    return *this;
  }
  template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
  DoubleNan& operator/=(T n) {
    value /= n;
    return *this;
  }
  template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
  DoubleNan& operator*=(T n) {
    value *= n;
    return *this;
  }
  DoubleNan operator+(const DoubleNan& n) const { return DoubleNan{value + n.value}; }
  DoubleNan operator-(const DoubleNan& n) const { return DoubleNan{value - n.value}; }
  DoubleNan operator/(const DoubleNan& n) const { return DoubleNan{value / n.value}; }
  DoubleNan operator*(const DoubleNan& n) const { return DoubleNan{value * n.value}; }
};

template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
inline DoubleNan operator+(T n1, const DoubleNan& n2) {
  return DoubleNan{static_cast<double>(n1) + n2.value};
}
template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
inline DoubleNan operator-(T n1, const DoubleNan& n2) {
  return DoubleNan{static_cast<double>(n1) - n2.value};
}
template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
inline DoubleNan operator/(T n1, const DoubleNan& n2) {
  return DoubleNan{static_cast<double>(n1) / n2.value};
}
template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
inline DoubleNan operator*(T n1, const DoubleNan& n2) {
  return DoubleNan{static_cast<double>(n1) * n2.value};
}

}  // namespace urx
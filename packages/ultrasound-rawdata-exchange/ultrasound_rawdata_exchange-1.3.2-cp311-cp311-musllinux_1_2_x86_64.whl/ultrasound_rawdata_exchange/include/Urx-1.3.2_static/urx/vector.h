#pragma once

namespace urx {

template <typename T>
struct Vector3D {
  using Type = T;

  bool operator==(const Vector3D<T>& other) const {
    return x == other.x && y == other.y && z == other.z;
  }

  bool operator!=(const Vector3D& other) const { return !operator==(other); }

  T x = 0.;
  T y = 0.;
  T z = 0.;
};

template <typename T>
struct Vector2D {
  using Type = T;

  bool operator==(const Vector2D<T>& other) const { return x == other.x && y == other.y; }

  bool operator!=(const Vector2D<T>& other) const { return !operator==(other); }

  T x = 0.;
  T y = 0.;
};

}  // namespace urx

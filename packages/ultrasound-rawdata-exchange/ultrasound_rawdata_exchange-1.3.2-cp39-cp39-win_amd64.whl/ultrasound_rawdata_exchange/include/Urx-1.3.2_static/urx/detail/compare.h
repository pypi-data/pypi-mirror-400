#pragma once

#include <algorithm>  // IWYU pragma: keep
#include <memory>
#include <vector>

namespace urx {

// SHARED == SHARED
template <typename T>
inline bool valueComparison(const std::shared_ptr<T>& lhs, const std::shared_ptr<T>& rhs) {
  return (lhs && rhs) ? (*lhs == *rhs) : (!!lhs == !!rhs);
}

// WEAK == WEAK
template <typename T>
inline bool valueComparison(const std::weak_ptr<T>& lhs, const std::weak_ptr<T>& rhs) {
  const std::shared_ptr<T>& lhs_lock = lhs.lock();
  const std::shared_ptr<T>& rhs_lock = rhs.lock();

  return (lhs_lock && rhs_lock) ? valueComparison(lhs_lock, rhs_lock) : (!!lhs_lock == !!rhs_lock);
}

// RAW PTR == RAW PTR
template <typename T>
inline bool valueComparison(const T* const lhs, const T* const rhs) {
  return (lhs && rhs) ? (*lhs == *rhs) : (!!lhs == !!rhs);
}

// SHARED == WEAK
template <typename T>
inline bool valueComparison(const std::shared_ptr<T>& lhs, const std::weak_ptr<T>& rhs) {
  return !rhs.expired() && valueComparison(lhs, rhs.lock());
}

template <typename T>
inline bool valueComparison(const std::weak_ptr<T>& lhs, const std::shared_ptr<T>& rhs) {
  return valueComparison(rhs, lhs);
}

// SHARED == RAW PTR
template <typename T>
inline bool valueComparison(const std::shared_ptr<T>& lhs, const T* const rhs) {
  return (lhs && rhs) ? (*lhs == *rhs) : (!!lhs == !!rhs);
}

template <typename T>
inline bool valueComparison(const T* const lhs, const std::shared_ptr<T>& rhs) {
  return valueComparison(rhs, lhs);
}

// WEAK == RAW PTR
template <typename T>
inline bool valueComparison(const std::weak_ptr<T>& lhs, const T* const rhs) {
  const std::shared_ptr<T>& lhs_lock = lhs.lock();

  return (lhs_lock && rhs) ? valueComparison(lhs_lock, rhs) : (!!lhs_lock == !!rhs);
}

template <typename T>
inline bool valueComparison(const T* const lhs, const std::weak_ptr<T>& rhs) {
  return valueComparison(rhs, lhs);
}

// VECTOR<T> == VECTOR<T>
template <typename T>
inline bool valueComparison(const std::vector<T>& lhs, const std::vector<T>& rhs) {
  return lhs == rhs;
}

// VECTOR<SHARED> == VECTOR<SHARED>
template <typename T>
inline bool valueComparison(const std::vector<std::shared_ptr<T>>& lhs,
                            const std::vector<std::shared_ptr<T>>& rhs) {
  return lhs.size() == rhs.size() &&
         std::equal(lhs.cbegin(), lhs.cend(), rhs.cbegin(), rhs.cend(),
                    [](const std::shared_ptr<T>& a, const std::shared_ptr<T>& b) {
                      return valueComparison(a, b);
                    });
}

// VECTOR<WEAK> == VECTOR<WEAK>
template <typename T>
inline bool valueComparison(const std::vector<std::weak_ptr<T>>& lhs,
                            const std::vector<std::weak_ptr<T>>& rhs) {
  return lhs.size() == rhs.size() &&
         std::equal(lhs.cbegin(), lhs.cend(), rhs.cbegin(), rhs.cend(),
                    [](const std::weak_ptr<T>& a, const std::weak_ptr<T>& b) {
                      return valueComparison(a, b);
                    });
}

// VECTOR<SHARED> == VECTOR<WEAK>
template <typename T>
inline bool valueComparison(const std::vector<std::shared_ptr<T>>& lhs,
                            const std::vector<std::weak_ptr<T>>& rhs) {
  return lhs.size() == rhs.size() &&
         std::equal(lhs.cbegin(), lhs.cend(), rhs.cbegin(), rhs.cend(),
                    [](const std::shared_ptr<T>& a, const std::weak_ptr<T>& b) {
                      return valueComparison(a, b);
                    });
}

// VECTOR<WEAK> == VECTOR<SHARED>
template <typename T>
inline bool valueComparison(const std::vector<std::weak_ptr<T>>& lhs,
                            const std::vector<std::shared_ptr<T>>& rhs) {
  return lhs.size() == rhs.size() &&
         std::equal(lhs.cbegin(), lhs.cend(), rhs.cbegin(), rhs.cend(),
                    [](const std::weak_ptr<T>& a, const std::shared_ptr<T>& b) {
                      return valueComparison(a, b);
                    });
}

}  // namespace urx
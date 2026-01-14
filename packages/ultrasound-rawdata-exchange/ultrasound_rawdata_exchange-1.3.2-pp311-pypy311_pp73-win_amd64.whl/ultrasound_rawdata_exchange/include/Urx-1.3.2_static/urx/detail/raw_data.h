#pragma once

#include <complex>
#include <cstdint>
#include <cstring>
#include <memory>
#include <unordered_map>
#include <vector>

#include <urx/detail/compare.h>  // IWYU pragma: keep
#include <urx/enums.h>
#include <urx/utils/cpp.h>

namespace urx {

namespace detail {

// Get DataType associated to type T
template <typename T>
struct DataTypeSelector {
  static constexpr DataType VALUE = DataType::UNDEFINED;
};

template <>
struct DataTypeSelector<double> {
  static constexpr DataType VALUE = DataType::DOUBLE;
};

template <>
struct DataTypeSelector<float> {
  static constexpr DataType VALUE = DataType::FLOAT;
};

template <>
struct DataTypeSelector<int32_t> {
  static constexpr DataType VALUE = DataType::INT32;
};

template <>
struct DataTypeSelector<int16_t> {
  static constexpr DataType VALUE = DataType::INT16;
};

template <typename T>
struct DataTypeSelector<std::complex<T>> {
  static constexpr DataType VALUE = DataTypeSelector<T>::VALUE;
};

}  // namespace detail

class RawData {
 public:
  virtual const void* getBuffer() const = 0;
  virtual void* getBuffer() = 0;
  virtual size_t getSize() const = 0;
  virtual SamplingType getSamplingType() const = 0;
  virtual DataType getDataType() const = 0;

  bool operator==(const RawData& other) const {
    // Also exist in urx::utils::group_helper::sizeofDataType.
    static std::unordered_map<DataType, size_t> group_dt_to_sizeof{
        {DataType::INT16, sizeof(int16_t)},
        {DataType::INT32, sizeof(int32_t)},
        {DataType::FLOAT, sizeof(float)},
        {DataType::DOUBLE, sizeof(double)}};
    return getSamplingType() == other.getSamplingType() && getDataType() == other.getDataType() &&
           getSize() == other.getSize() &&
           // Stream has null buffer. Suppose it's the same.
           (getSize() == 0 || getBuffer() == nullptr || other.getBuffer() == nullptr ||
            std::memcmp(getBuffer(), other.getBuffer(),
                        getSize() * group_dt_to_sizeof.at(getDataType()) *
                            (getSamplingType() == SamplingType::RF ? 1 : 2)) == 0);
  }
  bool operator!=(const RawData& other) const { return !operator==(other); }

  virtual ~RawData() = default;
};

template <typename T>
class IRawData : public RawData {
 public:
  SamplingType getSamplingType() const override {
    return utils::IsComplex<T>::value ? SamplingType::IQ : SamplingType::RF;
  };

  DataType getDataType() const override { return detail::DataTypeSelector<T>::VALUE; };

  const T* getTypedBuffer() const { return static_cast<const T*>(getBuffer()); };
  T* getTypedBuffer() { return static_cast<T*>(getBuffer()); };

  ~IRawData() override = default;
};

template <typename DataType>
class RawDataVector final : public IRawData<DataType> {
 public:
  explicit RawDataVector(std::vector<DataType>&& vector) : _vector(std::move(vector)) {}
  explicit RawDataVector(size_t size) : _vector(size) {}
  ~RawDataVector() override = default;

  const void* getBuffer() const override { return _vector.data(); }
  void* getBuffer() override { return _vector.data(); }
  size_t getSize() const override { return _vector.size(); }

 private:
  std::vector<DataType> _vector;
};

template <typename DataType>
class RawDataNoInit final : public IRawData<DataType> {
 public:
  explicit RawDataNoInit(size_t size) : _buffer(std::make_unique<DataType[]>(size)), _size(size) {}
  ~RawDataNoInit() override = default;

  const void* getBuffer() const override { return _buffer.get(); }
  void* getBuffer() override { return _buffer.get(); }
  size_t getSize() const override { return _size; }

 private:
  std::unique_ptr<DataType[]> _buffer;
  size_t _size;
};

template <typename DataType>
class RawDataWeak : public IRawData<DataType> {
 public:
  RawDataWeak(void* buffer, size_t size) : _buffer(buffer), _size(size) {}
  ~RawDataWeak() override = default;

  const void* getBuffer() const override { return _buffer; }
  void* getBuffer() override { return _buffer; }
  size_t getSize() const override { return _size; }

 protected:
  void* _buffer;
  size_t _size;
};

template <typename DataType>
class RawDataStream : public IRawData<DataType> {
 public:
  RawDataStream(size_t size) : _size(size) {}
  ~RawDataStream() override = default;

  const void* getBuffer() const override { return nullptr; }
  void* getBuffer() override { return nullptr; }
  size_t getSize() const override { return _size; }

 protected:
  size_t _size;
};

}  // namespace urx

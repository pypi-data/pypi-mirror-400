#ifndef MEMORY_ARENA_HPP
#define MEMORY_ARENA_HPP

#include <span>
#include <string>
#include <vector>
#include <cassert>
#include "helpers/log.hpp"

class TensorArena {
public:
  TensorArena() = default;
  TensorArena(const size_t size) {
    Logger::log("Reserving {} bytes from {} elements", size * sizeof(double), size);
    buffer.resize(size);
  }

  std::span<double> allocate(const size_t size) {
    assert("Allocating beyond vector's size" && offset + size <= buffer.size());
    std::span<double> span(buffer.data() + offset, size);
    offset += size;
    return span;
  }

  void resize(const size_t size) {
    buffer.resize(size);
  }

  void save(const std::string& save_path);
  void load(const std::string& load_path);
  void load(const std::vector<double>& load_buffer);
  const std::vector<double>& getBuffer() const { return buffer; }

private:
  std::vector<double> buffer;
  size_t offset = 0;
};

#endif // MEMORY_ARENA_HPP

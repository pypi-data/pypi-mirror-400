#include "helpers/tensorArena.hpp"
#include "helpers/log.hpp"
#include "helpers/exceptions.hpp"
#include <fstream>


void TensorArena::save(const std::string& save_path) {
  if (save_path.empty()) return;

  std::ofstream out(save_path, std::ios::binary);
  size_t size = buffer.size();

  out.write(reinterpret_cast<const char*>(&size), sizeof(size));
  out.write(reinterpret_cast<const char*>(buffer.data()), size * sizeof(double));
}

void TensorArena::load(const std::string& load_path) {
  if (load_path.empty()) return;

  Logger::log("Loading from: {}", load_path);
  std::ifstream in(load_path, std::ios::binary);
  if (!in) {
    throw NeuralNet::FileLoadError("Failed to open file for reading: " + load_path);
  }

  size_t size;
  in.read(reinterpret_cast<char*>(&size), sizeof(size));

  if (size != buffer.size()) {
    throw NeuralNet::BufferError(
      "Buffer size mismatch: file contains " + std::to_string(size) +
      " elements, but network expects " + std::to_string(buffer.size())
    );
  }

  in.read(reinterpret_cast<char*>(buffer.data()), size * sizeof(double));
}

void TensorArena::load(const std::vector<double>& load_buffer) {
  buffer.clear();
  buffer.reserve(load_buffer.size());

  for (double value : load_buffer) {
    buffer.push_back(value);
  }
}

#include "helpers/ModelPersist.hpp"
#include "helpers/log.hpp"
#include "helpers/formatting.hpp"
#include <iostream>
#include <fstream>

/**
 * TODO - This implementation is architecture specific, and a model
 * trained on x86 cannot be loaded/run on ARM due to big/little
 * Endian mis-match. NEED TO FIX
 */

ModelPersistStructure::ModelPersistStructure(const std::vector<Layer>& layers, 
                                             const std::vector<double>& tensors,
                                             const std::shared_ptr<Activations::Activation> hidden_activation,
                                             const std::shared_ptr<Activations::Activation> output_activation) {
  layers_ = layers.size();
  layer_counts_.resize(layers.size());
  for (size_t i = 0; i < layers.size(); i++) {
    layer_counts_[i] = layers[i].getSize();
  }

  tensor_buffer_double_count_ = tensors.size();
  tensor_buffer_ = tensors;

  hidden_activation_ = hidden_activation->getActivationValue();
  output_activation_ = output_activation->getActivationValue();
}

ModelPersistStructure::ModelPersistStructure(const std::string load_path) {
  load(load_path);
}

void ModelPersistStructure::persist(const std::string& save_path) {
  std::ofstream out(save_path, std::ios::binary);

  // Write layer count and layer sizes
  out.write(reinterpret_cast<const char*>(&layers_), sizeof(uint64_t));
  out.write(reinterpret_cast<const char*>(layer_counts_.data()), layers_* sizeof(uint64_t));

  // Write hidden activation enum value
  out.write(reinterpret_cast<const char*>(&hidden_activation_), sizeof(uint8_t));
  // Write output activation enum value
  out.write(reinterpret_cast<const char*>(&output_activation_), sizeof(uint8_t));

  // Write tensor buffer size and buffer
  out.write(reinterpret_cast<const char*>(&tensor_buffer_double_count_), sizeof(uint64_t));
  out.write(reinterpret_cast<const char*>(tensor_buffer_.data()), tensor_buffer_double_count_* sizeof(double));
}

void ModelPersistStructure::load(const std::string& load_path) {
    std::ifstream in(load_path, std::ios::binary);
    if (!in) throw std::runtime_error("Failed to open file for reading: " + load_path);

    // Read layer count
    in.read(reinterpret_cast<char*>(&layers_), sizeof(uint64_t));
    Logger::debug("Read layer count: {}", layers_);

    // Read layer sizes
    layer_counts_.resize(layers_);
    in.read(reinterpret_cast<char*>(layer_counts_.data()), layers_* sizeof(uint64_t));
    Logger::debug("Read layer sizes: {}", Formatting::formatVector(layer_counts_));

    // Read hidden activation value
    in.read(reinterpret_cast<char*>(&hidden_activation_), sizeof(uint8_t));
    // Read output activation value
    in.read(reinterpret_cast<char*>(&output_activation_), sizeof(uint8_t));

    // Read tensor buffer
    in.read(reinterpret_cast<char*>(&tensor_buffer_double_count_), sizeof(uint64_t));
    Logger::debug("Read tensor count: {}", tensor_buffer_double_count_);
    tensor_buffer_.resize(tensor_buffer_double_count_);
    in.read(reinterpret_cast<char*>(tensor_buffer_.data()), tensor_buffer_double_count_ * sizeof(double));
    Logger::debug("Read tensor buffer: {}", tensor_buffer_.size());
}

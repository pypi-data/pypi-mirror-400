#ifndef MODEL_PERSIST_HPP
#define MODEL_PERSIST_HPP

#include <cstdint>
#include <vector>
#include <string>
#include "components/layer.hpp"
#include "helpers/activations.hpp"

class ModelPersistStructure {
public:
  ModelPersistStructure(const std::vector<Layer>& layers, 
                        const std::vector<double>& tensors,
                        const std::shared_ptr<Activations::Activation> hidden_activation,
                        const std::shared_ptr<Activations::Activation> output_activation);
  ModelPersistStructure(const std::string load_path);
  ModelPersistStructure() = default;

  void persist(const std::string& save_path);
  void load(const std::string& load_path);

  const std::vector<uint64_t>& getLayers() const { return layer_counts_; }
  const std::vector<double>& getTensors() const { return tensor_buffer_; }
  const Activations::ActivationEnum getHiddenActivation() const {
    return hidden_activation_; 
  }
  const Activations::ActivationEnum getOutputActivation() const {
    return output_activation_; 
  }
private:
  uint64_t layers_;                        // 64 bits
  std::vector<uint64_t> layer_counts_;     // 64 * layers

  Activations::ActivationEnum hidden_activation_;
  Activations::ActivationEnum output_activation_;

  uint64_t tensor_buffer_double_count_;    // 64 bits
  std::vector<double> tensor_buffer_;      // 64 * tensor_buffer_double_count
};

#endif

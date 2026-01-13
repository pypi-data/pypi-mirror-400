#ifndef NETWORK_H
#define NETWORK_H

#include "components/layer.hpp"
#include "helpers/activations.hpp"
#include "helpers/tensorArena.hpp"
#include "training/dataset.hpp"

class ActivationBundle;
class Dataset;
class Optimizer;

class Network {
public:
  Network(const std::vector<uint64_t> layers,
          const std::shared_ptr<Activations::Activation> hidden_activation,
          const std::shared_ptr<Activations::Activation> output_activation);

  Network(const std::vector<uint64_t> layers,
          const Activations::ActivationEnum hidden_activation_enum,
          const Activations::ActivationEnum output_activation_enum);

  Network(const std::vector<uint64_t> layers,
          const std::shared_ptr<Activations::Activation> hidden_activation,
          const std::shared_ptr<Activations::Activation> output_activation,
          const std::vector<double>& tensors);

  Network(const std::vector<uint64_t> layers,
          const Activations::ActivationEnum hidden_activation,
          const Activations::ActivationEnum output_activation,
          const std::vector<double>& tensors);

  ~Network();

  // Delete Copy and Move constructors
  Network(const Network&) = delete;
  Network& operator=(const Network&) = delete;
  Network(Network&&) = default;
  Network& operator=(Network&&) = default;

  // Feed-forward
  void forward(std::vector<double> input);
  void forward(std::span<double> input);

  // Backward
  void backward(std::span<double> target, const std::shared_ptr<Losses::Loss> loss);
  void updateWeights(const double learning_rate,
                     const size_t batch_index,
                     const size_t timestep);

  // Getters
  std::vector<Layer>& getLayers() { return layers_; }
  const std::vector<Layer>& getLayers() const { return layers_; }
  const std::span<double> getOutput() const { 
    return layers_.at(layers_.size() - 1).getValues();
  }
  const TensorArena& getTensorArena() const {
    return tensor_arena;
  }
  const std::shared_ptr<Activations::Activation> getHiddenActivation() const {
    return hidden_activation_;
  }
  const std::shared_ptr<Activations::Activation> getOutputActivation() const {
    return output_activation_;
  }

private:
  inline size_t calculate_arena_size(const std::vector<uint64_t>& layers);
  void initialize_layers(const std::vector<uint64_t>& layers,
                         const std::shared_ptr<Activations::Activation> hidden_activation,
                         const std::shared_ptr<Activations::Activation> output_activation);
  void validate_layer_configuration(const std::vector<uint64_t>& layers) const;
  void validate_activations(const std::shared_ptr<Activations::Activation> hidden_activation,
                           const std::shared_ptr<Activations::Activation> output_activation) const;

  size_t size;

  std::vector<Layer> layers_;

  const std::shared_ptr<Activations::Activation> hidden_activation_;
  const std::shared_ptr<Activations::Activation> output_activation_;

  TensorArena tensor_arena;

  friend Layer;
};

#endif

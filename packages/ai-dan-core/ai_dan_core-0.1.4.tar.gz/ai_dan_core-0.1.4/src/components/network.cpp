#include "components/network.hpp"
#include "helpers/exceptions.hpp"
#include <span>

Network::Network(const std::vector<uint64_t> layers,
                 const std::shared_ptr<Activations::Activation> hidden_activation,
                 const std::shared_ptr<Activations::Activation> output_activation)
                 : size(layers.size()),
                   tensor_arena(calculate_arena_size(layers)),
                   hidden_activation_(hidden_activation),
                   output_activation_(output_activation) {
  initialize_layers(layers, hidden_activation_, output_activation_);
}

Network::Network(const std::vector<uint64_t> layers,
                 const Activations::ActivationEnum hidden_activation_enum,
                 const Activations::ActivationEnum output_activation_enum)
                 : size(layers.size()),
                   tensor_arena(calculate_arena_size(layers)),
                   hidden_activation_(Activations::activationMap.at(hidden_activation_enum)),
                   output_activation_(Activations::activationMap.at(output_activation_enum)) {
  initialize_layers(layers, hidden_activation_, output_activation_);
}

Network::Network(const std::vector<uint64_t> layers,
                 const std::shared_ptr<Activations::Activation> hidden_activation,
                 const std::shared_ptr<Activations::Activation> output_activation,
                 const std::vector<double>& tensors)
                 : Network(layers, hidden_activation, output_activation) {
  tensor_arena.load(tensors);
}

Network::Network(const std::vector<uint64_t> layers,
                 const Activations::ActivationEnum hidden_activation,
                 const Activations::ActivationEnum output_activation,
                 const std::vector<double>& tensors)
                 : Network(layers, hidden_activation, output_activation) {
  tensor_arena.load(tensors);
}

Network::~Network() {}

void Network::forward(std::vector<double> input) {
  forward(std::span(input.data(), input.size()));
}

void Network::forward(std::span<double> input) {
  if (input.size() != layers_[0].size) {
    throw NeuralNet::InvalidInputError(
      "Input vector size (" + std::to_string(input.size()) +
      ") does not match input layer size (" + std::to_string(layers_[0].size) + ")"
    );
  }
  layers_[0].values = input;

  for (size_t i = 1; i < layers_.size(); i++) {
    layers_.at(i).forward(ThreadPool::global());
  }
}

void Network::backward(std::span<double> target, const std::shared_ptr<Losses::Loss> loss) {
  if (target.size() != layers_.at(size-1).size) {
    throw NeuralNet::InvalidTargetError(
      "Target vector size (" + std::to_string(target.size()) +
      ") does not match output layer size (" + std::to_string(layers_.at(size-1).size) + ")"
    );
  }

  // Use loss + output layer activation to compute deltas
  layers_[size - 1].computeDeltas(target, ThreadPool::global(), loss);
  layers_[size - 1].computeGradients(ThreadPool::global());

  // Prop deltas backwards
  for (size_t i = size - 2; i > 0; i--) {
    layers_.at(i).computeDeltas(ThreadPool::global());
    layers_.at(i).computeGradients(ThreadPool::global());
  }
}

void Network::updateWeights(const double learning_rate,
                            const size_t batch_size,
                            const size_t timestep) {
  // Update weights
  for (size_t i = 1; i < size; i++) {
    layers_.at(i).updateWeights(ThreadPool::global(), learning_rate, batch_size, timestep);
  }
}

void Network::initialize_layers(const std::vector<uint64_t>& layers,
                                const std::shared_ptr<Activations::Activation> hidden_activation,
                                const std::shared_ptr<Activations::Activation> output_activation) {
  validate_layer_configuration(layers);
  validate_activations(hidden_activation, output_activation);

  layers_.reserve(size),
  // Input layer does not have an activation
  Logger::debug("Creating input layer");
  layers_.emplace_back(layers[0], this);

  for (size_t i = 1; i < layers.size(); ++i) {
    Logger::debug("Creating layer: {}", i);
    const std::shared_ptr<Activations::Activation> layer_activation_bundle 
      = (i == layers.size() - 1) ? output_activation : hidden_activation;

    layers_.emplace_back(layers[i], this, &layers_[i - 1], i, layer_activation_bundle);

    layers_[i - 1].next_layer = &layers_[i];
  }
}

void Network::validate_layer_configuration(const std::vector<uint64_t>& layers) const {
  if (layers.empty()) {
    throw NeuralNet::LayerConfigurationError("Network must have at least one layer");
  }
  if (layers.size() < 2) {
    throw NeuralNet::LayerConfigurationError("Network must have at least an input and output layer");
  }
  for (size_t i = 0; i < layers.size(); i++) {
    if (layers[i] == 0) {
      throw NeuralNet::LayerConfigurationError(
        "Layer " + std::to_string(i) + " has size 0, all layers must have size > 0"
      );
    }
  }
}

void Network::validate_activations(const std::shared_ptr<Activations::Activation> hidden_activation,
                                    const std::shared_ptr<Activations::Activation> output_activation) const {
  if (!hidden_activation) {
    throw NeuralNet::LayerConfigurationError("Hidden activation cannot be null");
  }
  if (!output_activation) {
    throw NeuralNet::LayerConfigurationError("Output activation cannot be null");
  }
}

size_t Network::calculate_arena_size(const std::vector<uint64_t>& layers) {
  size_t size = 0;

  // Input layer only has values
  size += layers[0];
  for (size_t i = 1; i < layers.size(); i++) {
    size += layers[i];                     // values
    size += layers[i];                     // pre-activated-values
    size += layers[i];                     // biases
    
    size += layers[i] * layers[i - 1];     // Weights
    size += layers[i] * layers[i - 1];     // variance
    size += layers[i] * layers[i - 1];     // momentum 

    size += layers[i];                     // bias momentum
    size += layers[i];                     // bias variance
    
    size += layers[i];                     // deltas
    size += layers[i] * layers[i - 1];     // accumulated gradients throughout batch
    size += layers[i];                     // accumulated bias
  }

  return size;
}

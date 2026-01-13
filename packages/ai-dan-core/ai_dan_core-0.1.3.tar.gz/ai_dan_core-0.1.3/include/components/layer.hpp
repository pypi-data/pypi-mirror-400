#ifndef LAYER_H
#define LAYER_H

#include "helpers/activations.hpp"
#include "helpers/loss.hpp"
#include "helpers/threadPool.hpp"
#include "helpers/math.hpp"
#include "helpers/exceptions.hpp"
#include <span>

class Layer {
public:
  Layer(size_t nodes,
        Network* network,
        Layer* previous_layer, 
        size_t layer_position,
        const std::shared_ptr<Activations::Activation> activation);

  Layer(size_t nodes,
        Network* network);

  ~Layer();

  // Delete Copy and Move constructors
  Layer(const Layer&) = delete;
  Layer& operator=(const Layer&) = delete;
  Layer(Layer&&) = default;
  Layer& operator=(Layer&&) = default;

  // Feed-Forward
  void forward(ThreadPool& thread_pool);

  // Back-Propagation
  void computeDeltas(std::span<double> target, 
                     ThreadPool& thread_pool, 
                     const std::shared_ptr<Losses::Loss> loss);
  void computeDeltas(ThreadPool& thread_pool);
  void computeGradients(ThreadPool& thread_pool);
  void updateWeights(ThreadPool& thread_pool, 
                     const double learning_rate, 
                     const size_t batch_size,
                     const size_t timestep);
  void clearGradients();

  size_t getSize() const { return values.size(); }
  double getValue(const size_t index) const {
    if (index >= values.size()) {
      throw NeuralNet::InvalidInputError(
        "Index " + std::to_string(index) + " out of range (size: " + std::to_string(values.size()) + ")"
      );
    }
    return values[index];
  }
  const std::span<double>& getValues() const { return values; }
  double getPreActivatedValue(const size_t index) const {
    if (index >= pre_activated_values.size()) {
      throw NeuralNet::InvalidInputError(
        "Index " + std::to_string(index) + " out of range (size: " + std::to_string(pre_activated_values.size()) + ")"
      );
    }
    return pre_activated_values[index];
  }
  std::span<double> getDeltas() const { return deltas_; }
  
  // Pointers to surrounding elements
  const Network* network;
  const Layer* previous_layer;
  const Layer* next_layer;
private:
  // Used for feed-forward
  std::span<double> values;
  std::span<double> pre_activated_values;
  std::span<double> weights;
  std::span<double> bias;

  std::span<double> variance;
  std::span<double> momentum;
  std::span<double> bias_variance;
  std::span<double> bias_momentum;

  std::span<double> deltas_;

  std::span<double> accumulated_gradients_;
  std::span<double> bias_accumulated_gradient_;

  const std::shared_ptr<Activations::Activation> activation_;
  
  // Private helper const's
  const size_t layer_position;
  const size_t input_size;
  const size_t size;

  // Private inline helper function
  inline double calculateValue(const size_t node);
  inline void accumulateNodeGradientAndBias(const size_t node);
  inline void updateNodeWeightsAndBias(size_t node,
                                       const double learning_rate,
                                       const size_t batch_size,
                                       const size_t timestep);
  inline size_t getWeightIndexForNode(const size_t node, const size_t input_node) {
    return input_size * node + input_node;
  }

  // Helper functions for computeDeltas to improve readability
  void initializeDeltasBlock(const size_t block_start, const size_t block_end);
  void accumulateNextLayerContributions(const size_t i_block_start,
                                        const size_t i_block_end,
                                        const size_t TILE_SIZE);
  void applyActivationDerivative(const size_t block_start, const size_t block_end);
  void processNeuronBlock(const size_t block_start,
                          const size_t block_end,
                          const size_t TILE_SIZE);

  // Math friend functions
  friend void Math::sigmoid_layer(Layer&, ThreadPool&);
  friend void Math::relu_layer(Layer&, ThreadPool&);
  friend void Math::leaky_relu_layer(Layer&, ThreadPool&);
  friend void Math::tanh_layer(Layer&, ThreadPool&);
  friend void Math::softmax_layer(Layer&, ThreadPool&);

  friend double Math::xavier_initialization(const Network& network, const Layer& layer);
  friend double Math::he_init_initialization(const Network& network, const Layer& layer);

  friend Network;
};

#endif

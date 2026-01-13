#include "components/network.hpp"
#include "components/layer.hpp"
#include "helpers/math.hpp"
#include "helpers/log.hpp"
#include "helpers/constants.hpp"
#include "helpers/exceptions.hpp"
#include <latch>
#include <cmath>

Layer::Layer(size_t size,
             Network* network,
             Layer* previous_layer, 
             size_t layer_position,
             const std::shared_ptr<Activations::Activation> activation) 
             : size(size),
               input_size(previous_layer->size),
               network(network),
               previous_layer(previous_layer),
               layer_position(layer_position),
               activation_(activation) {
  // Feed-Forward
  values =                      network->tensor_arena.allocate(size); // Values
  pre_activated_values =        network->tensor_arena.allocate(size); // Pre-Activated Values
  bias =                        network->tensor_arena.allocate(size); // Bias

  // Back-prop
  // Deltas
  deltas_ =                     network->tensor_arena.allocate(size);
  // Accumulated gradient per weight over batch 
  accumulated_gradients_ =      network->tensor_arena.allocate(size * previous_layer->size);
  // accumulated bias per node 
  bias_accumulated_gradient_ =  network->tensor_arena.allocate(size);

  // Momenmtum
  weights =               network->tensor_arena.allocate(size * previous_layer->size); // Weights
  variance =              network->tensor_arena.allocate(size * previous_layer->size); // Variance
  momentum =              network->tensor_arena.allocate(size * previous_layer->size); // Momentum

  // Bias Momentum
  bias_momentum =         network->tensor_arena.allocate(size); // Bias-Momentum
  bias_variance =         network->tensor_arena.allocate(size); // Bias-Variance

  for (size_t i = 0; i < weights.size(); i++) {
    weights[i] = activation_->initializeWeights(*network, *this);
  }

  for (size_t i = 0; i < values.size(); i++) {
    bias[i] = 0.0;
  }
}

Layer::Layer(size_t size,
             Network* network)
             : size(size),
               input_size(0),
               network(network),
               layer_position(0),
               activation_(nullptr) {
  Logger::log("Creating layer of size: {}", size);
  values = network->tensor_arena.allocate(size);
  Logger::log("Values: {}", values.size());
}

Layer::~Layer() {
  
}

void Layer::forward(ThreadPool& thread_pool) {
  // Adaptive parallelism: only use threading if layer is large enough
  const size_t num_threads = ThreadingUtils::getOptimalThreadCount(size);

  if (num_threads == 1) {
    // Serial execution for small layers - no synchronization overhead
    for (size_t node = 0; node < size; node++) {
      pre_activated_values[node] = calculateValue(node);
    }
  } else {
    // Parallel execution for large layers
    const size_t chunk_size = (size + num_threads - 1) / num_threads;
    std::latch done(num_threads);

    for (size_t t = 0; t < num_threads; t++) {
      thread_pool.enqueue([&, t] () {
        const size_t start = t * chunk_size;
        const size_t end = std::min(start + chunk_size, size);

        for (size_t node = start; node < end; node++) {
          pre_activated_values[node] = calculateValue(node);
        }

        done.count_down();
      });
    }

    done.wait();
  }

  if (activation_) {
    activation_->activate(*this, thread_pool);
  }
}

void Layer::computeDeltas(std::span<double> target, 
                          ThreadPool& thread_pool,
                          const std::shared_ptr<Losses::Loss> loss) {
  if (activation_) {
    loss->delta(this, thread_pool, target, activation_);
  }
}

void Layer::initializeDeltasBlock(const size_t block_start, const size_t block_end) {
  for (size_t i = block_start; i < block_end; i++) {
    deltas_[i] = 0.0;
  }
}

void Layer::accumulateNextLayerContributions(const size_t i_block_start,
                                              const size_t i_block_end,
                                              const size_t TILE_SIZE) {
  // Process next layer neurons in blocks for cache efficiency
  for (size_t j_block = 0; j_block < next_layer->size; j_block += TILE_SIZE) {
    const size_t j_block_end = std::min(j_block + TILE_SIZE, next_layer->size);

    // Accumulate contributions from each neuron in the next layer
    for (size_t j = j_block; j < j_block_end; j++) {
      const double delta_j = next_layer->deltas_[j];
      const double* weight_row = &next_layer->weights[j * size];

      // Vectorizable loop: accumulate weighted deltas
      #pragma GCC ivdep
      for (size_t i = i_block_start; i < i_block_end; i++) {
        deltas_[i] += delta_j * weight_row[i];
      }
    }
  }
}

void Layer::applyActivationDerivative(const size_t block_start, const size_t block_end) {
  if (!activation_) return;

  for (size_t i = block_start; i < block_end; i++) {
    deltas_[i] *= activation_->derive(pre_activated_values[i], values[i]);
  }
}

void Layer::processNeuronBlock(const size_t block_start,
                                const size_t block_end,
                                const size_t TILE_SIZE) {
  initializeDeltasBlock(block_start, block_end);
  accumulateNextLayerContributions(block_start, block_end, TILE_SIZE);
  applyActivationDerivative(block_start, block_end);
}

void Layer::computeDeltas(ThreadPool& thread_pool) {
  const size_t num_threads = ThreadingUtils::getOptimalThreadCount(size);

  if (num_threads == 1) {
    // Serial execution for small layers
    constexpr size_t TILE_SIZE = 64;
    for (size_t i_block = 0; i_block < size; i_block += TILE_SIZE) {
      const size_t i_block_end = std::min(i_block + TILE_SIZE, size);
      processNeuronBlock(i_block, i_block_end, TILE_SIZE);
    }
  } else {
    // Parallel execution for large layers
    const size_t chunk_size = (size + num_threads - 1) / num_threads;
    std::latch done(num_threads);

    for (size_t t = 0; t < num_threads; t++) {
      thread_pool.enqueue([&, t] () {
        const size_t start = t * chunk_size;
        const size_t end = std::min(start + chunk_size, size);

        constexpr size_t TILE_SIZE = 64;
        for (size_t i_block = start; i_block < end; i_block += TILE_SIZE) {
          const size_t i_block_end = std::min(i_block + TILE_SIZE, end);
          processNeuronBlock(i_block, i_block_end, TILE_SIZE);
        }

        done.count_down();
      });
    }

    done.wait();
  }
}

void Layer::computeGradients(ThreadPool& thread_pool) {
  const size_t num_threads = ThreadingUtils::getOptimalThreadCount(size);

  if (num_threads == 1) {
    // Serial execution for small layers
    for (size_t i = 0; i < size; i++) {
      accumulateNodeGradientAndBias(i);
    }
  } else {
    // Parallel execution for large layers
    const size_t chunk_size = (size + num_threads - 1) / num_threads;
    std::latch done(num_threads);

    for (size_t t = 0; t < num_threads; t++) {
      thread_pool.enqueue([&, t] () {
        const size_t start = t * chunk_size;
        const size_t end = std::min(start + chunk_size, size);

        for (size_t i = start; i < end; i++) {
          accumulateNodeGradientAndBias(i);
        }

        done.count_down();
      });
    }

    done.wait();
  }
}

void Layer::accumulateNodeGradientAndBias(const size_t node) {
  const double delta = deltas_[node];
  const double* input_ptr = previous_layer->values.data();
  double* grad_row = &accumulated_gradients_[node * previous_layer->size];

  // vectorize loop
  #pragma GCC ivdep
  for (size_t i = 0; i < input_size; ++i) {
    grad_row[i] += delta * input_ptr[i];
  }

  // Bias term
  bias_accumulated_gradient_[node] += delta;
}

void Layer::updateWeights(ThreadPool& thread_pool,
                          const double learning_rate,
                          const size_t batch_size,
                          const size_t timestep) {
  const size_t num_threads = ThreadingUtils::getOptimalThreadCount(size);

  if (num_threads == 1) {
    // Serial execution for small layers
    for (size_t i = 0; i < size; i++) {
      updateNodeWeightsAndBias(i, learning_rate, batch_size, timestep);
    }
  } else {
    // Parallel execution for large layers
    const size_t chunk_size = (size + num_threads - 1) / num_threads;
    std::latch done(num_threads);

    for (size_t t = 0; t < num_threads; t++) {
      thread_pool.enqueue([&, t] () {
        const size_t start = t * chunk_size;
        const size_t end = std::min(start + chunk_size, size);

        for (size_t i = start; i < end; i++) {
          updateNodeWeightsAndBias(i, learning_rate, batch_size, timestep);
        }

        done.count_down();
      });
    }

    done.wait();
  }

  clearGradients();
}

void Layer::clearGradients() {
  std::fill(accumulated_gradients_.begin(), accumulated_gradients_.end(), 0.0);
  std::fill(bias_accumulated_gradient_.begin(), bias_accumulated_gradient_.end(), 0.0);
}

void Layer::updateNodeWeightsAndBias(size_t node, 
                                     const double learning_rate, 
                                     const size_t batch_size,
                                     const size_t timestep) {
  const double beta1 = Constants::momentum_coefficient;
  const double beta2 = Constants::momentum_coefficient_variance;
  const double eps = 1e-8;

  const double beta1_t_pow = std::pow(beta1, timestep);
  const double beta2_t_pow = std::pow(beta2, timestep);

  // const double batch_delta = Math::average_span(std::span<double>(batch_deltas.data() + (size * node), size));
  const double batch_delta = deltas_[node];

  for (size_t i = 0; i < input_size; ++i) {
    // TODO: I dont think batch gradient descent is correctly implemented here
    // Need to introduct averaging the gradients over the batch
    double grad = accumulated_gradients_[node * previous_layer->size + i] / batch_size;
    grad = std::clamp(grad, -Constants::gradient_clip, Constants::gradient_clip);
    const size_t idx = getWeightIndexForNode(node, i);

    // Update biased moment estimates
    momentum[idx] = beta1 * momentum[idx] + (1.0 - beta1) * grad;
    variance[idx] = beta2 * variance[idx] + (1.0 - beta2) * grad * grad;

    // Bias correction
    const double m_hat = momentum[idx] / (1.0 - beta1_t_pow);
    const double v_hat = variance[idx] / (1.0 - beta2_t_pow);

    // Weight update
    weights[idx] -= learning_rate * m_hat / (std::sqrt(v_hat) + eps);
  }

  // Bias term
  double grad_b = bias_accumulated_gradient_[node] / batch_size;
  grad_b = std::clamp(grad_b, -Constants::gradient_clip, Constants::gradient_clip);
  bias_momentum[node] = beta1 * bias_momentum[node] + (1.0 - beta1) * grad_b;
  bias_variance[node] = beta2 * bias_variance[node] + (1.0 - beta2) * grad_b * grad_b;

  const double m_hat_b = bias_momentum[node] / (1.0 - beta1_t_pow);
  const double v_hat_b = bias_variance[node] / (1.0 - beta2_t_pow);

  bias[node] -= learning_rate * m_hat_b / (std::sqrt(v_hat_b) + eps);
}

double Layer::calculateValue(const size_t node) {
  const std::span<double> input = previous_layer->values;
  const size_t expected_size = weights.size() / values.size();
  if (input.size() != expected_size) {
    throw NeuralNet::LayerConfigurationError(
      "Input vector size (" + std::to_string(input.size()) +
      ") does not match expected size (" + std::to_string(expected_size) + ")"
    );
  }

  double output = bias[node];
  const double* weight_row = &weights[node * input_size];  // Cache-friendly pointer
  const double* input_ptr = input.data();

  // Compiler hint: this loop can be vectorized
  #pragma GCC ivdep
  for (size_t i = 0; i < input.size(); i++) {
    output += input_ptr[i] * weight_row[i];
  }

  return output;
}


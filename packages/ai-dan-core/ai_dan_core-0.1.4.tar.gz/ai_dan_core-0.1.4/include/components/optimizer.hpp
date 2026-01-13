#ifndef OPTIMIZER_HPP
#define OPTIMIZER_HPP

#include "components/network.hpp"
#include "helpers/exceptions.hpp"

class Optimizer {
public:
  Optimizer(const double learning_rate, const size_t batch_size)
    : learning_rate_(learning_rate),
      batch_size_(batch_size) {
    if (learning_rate <= 0.0) {
      throw NeuralNet::OptimizerError(
        "Learning rate must be positive, got " + std::to_string(learning_rate)
      );
    }
    if (batch_size == 0) {
      throw NeuralNet::OptimizerError("Batch size must be greater than 0");
    }
  }

  void step(Network& network) {
    network.updateWeights(learning_rate_, batch_size_, timestep_);
    timestep_++;
  }

  void resetGradients(Network& network) const {
    for (Layer& layer : network.getLayers()) {
      layer.clearGradients();
    }
  }

  double getLearningRate() const { return learning_rate_; }
  size_t getBatchSize() const { return batch_size_; }

private:
  const double learning_rate_;
  const size_t batch_size_;
  size_t timestep_ = 1;
};

#endif

#include "helpers/math.hpp"
#include "helpers/random.hpp"
#include "helpers/constants.hpp"
#include "helpers/exceptions.hpp"
#include "components/layer.hpp"
#include "components/network.hpp"

#include <latch>
#include <numeric>

/** SIGMOID */
void Math::sigmoid_layer(Layer& layer, ThreadPool& thread_pool) {
  const size_t num_threads = ThreadingUtils::getOptimalThreadCount(layer.size);

  if (num_threads == 1) {
    // Serial execution
    for (size_t i = 0; i < layer.size; i++) {
      layer.values[i] = sigmoid(layer.pre_activated_values[i]);
    }
  } else {
    // Parallel execution
    const size_t chunk_size = (layer.size + num_threads - 1) / num_threads;
    std::latch done(num_threads);

    for (size_t t = 0; t < num_threads; t++) {
      thread_pool.enqueue([&, t] () {
        const size_t start = t * chunk_size;
        const size_t end = std::min(start + chunk_size, layer.size);

        for (size_t i = start; i < end; i++) {
          layer.values[i] = sigmoid(layer.pre_activated_values[i]);
        }

        done.count_down();
      });
    }

    done.wait();
  }
}

double Math::sigmoid(const double x) {
  return 1.0 / (1.0 + std::exp(-x));
}

double Math::sigmoid_derivative(const double, const double activated_output) {
  return activated_output * (1.0 - activated_output);
}

/** RELU*/
void Math::relu_layer(Layer& layer, ThreadPool& thread_pool) {
  const size_t num_threads = ThreadingUtils::getOptimalThreadCount(layer.size);

  if (num_threads == 1) {
    // Serial execution
    for (size_t i = 0; i < layer.size; i++) {
      layer.values[i] = relu(layer.pre_activated_values[i]);
    }
  } else {
    // Parallel execution
    const size_t chunk_size = (layer.size + num_threads - 1) / num_threads;
    std::latch done(num_threads);

    for (size_t t = 0; t < num_threads; t++) {
      thread_pool.enqueue([&, t] () {
        const size_t start = t * chunk_size;
        const size_t end = std::min(start + chunk_size, layer.size);

        for (size_t i = start; i < end; i++) {
          layer.values[i] = relu(layer.pre_activated_values[i]);
        }

        done.count_down();
      });
    }

    done.wait();
  }
}

double Math::relu(const double x) {
  return x > 0 ? x : 0;
}

double Math::relu_derivative(const double pre_activated_output, const double) {
  return pre_activated_output > 0 ? 1 : 0;
}

/** LEAKY RELU*/
void Math::leaky_relu_layer(Layer& layer, ThreadPool& thread_pool) {
  const size_t num_threads = ThreadingUtils::getOptimalThreadCount(layer.size);

  if (num_threads == 1) {
    // Serial execution
    for (size_t i = 0; i < layer.size; i++) {
      layer.values[i] = leaky_relu(layer.pre_activated_values[i]);
    }
  } else {
    // Parallel execution
    const size_t chunk_size = (layer.size + num_threads - 1) / num_threads;
    std::latch done(num_threads);

    for (size_t t = 0; t < num_threads; t++) {
      thread_pool.enqueue([&, t] () {
        const size_t start = t * chunk_size;
        const size_t end = std::min(start + chunk_size, layer.size);

        for (size_t i = start; i < end; i++) {
          layer.values[i] = leaky_relu(layer.pre_activated_values[i]);
        }

        done.count_down();
      });
    }

    done.wait();
  }
}

double Math::leaky_relu(const double x) {
  return (x > 0) ? x : (Constants::leaky_relu_alpha * x);
}

double Math::leak_relu_derivative(const double pre_activated_output, const double activated_output) {
  return pre_activated_output > 0 ? 1.0 : Constants::leaky_relu_alpha;
}

/** TANH */
void Math::tanh_layer(Layer& layer, ThreadPool& thread_pool) {
  throw NeuralNet::NotImplementedError("tanh_layer activation is not yet implemented");
}

double Math::tanh(const double x) {
  return std::tanh(x);
}

double Math::tanh_derivative(const double, const double activated_output) {
  return 1.0 - activated_output * activated_output;
}

/** SOFTMAX */
void Math::softmax_layer(Layer& layer, ThreadPool&) {
  const std::span<double>& PAV = layer.pre_activated_values;
  std::span<double> values = layer.values;

  double max_val = *std::max_element(PAV.begin(), 
      PAV.end());

  double sum_exp = 0.0;
  for (size_t i = 0; i < PAV.size(); i++) {
    values[i] = std::exp(PAV[i] - max_val);
    sum_exp += values[i];
  }

  for (size_t i = 0; i < values.size(); i++) {
    values[i] /=  sum_exp;
  }
}

double Math::softmax_derivative(const double, const double) {
  throw NeuralNet::NotImplementedError("softmax_derivative is not yet implemented");
  return -1;
}

/** WEIGHT INITIALIZATION */
double Math::xavier_initialization(const Network& network, const Layer& layer) {
  const size_t fan_in = layer.previous_layer != nullptr ? layer.previous_layer->size : 1;
  size_t fan_out = layer.size;
  double limit = std::sqrt(6.0 / (fan_in + fan_out));
  return Random::getDouble(-limit, limit);
}

double Math::he_init_initialization(const Network&, const Layer& layer) {
  int fan_in = layer.previous_layer ? layer.previous_layer->size : 1;
  double limit = std::sqrt(2.0 / static_cast<double>(fan_in));
  return Random::getDouble(-limit, limit);
}

/** RANDOM HELPERS */
void Math::get_random_vector(std::span<double> input_span, const size_t size) {
  for (size_t i = 0; i < size; i++) {
    input_span[i] = Random::getDouble(0, 1);
  }
}

double Math::average_span(std::span<double> input) {
  double sum = 0;
  for (double i : input) { sum += i; }

  return sum / static_cast<double>(input.size());
}

double Math::getStandardDeviation(std::span<double> input, const double mean) {

  double squared_sum = 0.0;
  for (double val : input) {
    squared_sum += (val - mean) * (val - mean);
  }
  return std::sqrt(squared_sum / input.size());
}

void Math::normalize(std::span<double> input) {
  double sum = std::accumulate(input.begin(), input.end(), 0.0);
  double mean = sum / input.size();
  const double standard_deviation = getStandardDeviation(input, mean);

  for (double& val : input) {
    val = (val - mean) / (standard_deviation + 1e-8);
  }
}

#ifndef CONSTANTS_HPP
#define CONSTANTS_HPP

#include <string>

namespace Constants {
  enum LOG_LEVEL { DEBUG, INFO, WARN, ERROR, FATAL };
  constexpr const char* LOG_LEVEL_STRING[] = { "DEBUG", "INFO", "WARN", "ERROR", "FATAL" };

  static const bool log_enabled = true;
  static const bool lock_logging = false;
  static const LOG_LEVEL log_level = LOG_LEVEL::INFO;

  static const std::string  websocket_domain = "localhost";
  static const std::string  websocket_port = "8765";

  static const double leaky_relu_alpha = 0.001;

  static const std::string MNIST_TRAINING_IMAGES_PATH = "/home/aidan/workspace/ai-dan-cpp/src/trainingDatasets/data/MNIST/train-images.idx3-ubyte";
  static const std::string MNIST_TRAINING_LABELS_PATH = "/home/aidan/workspace/ai-dan-cpp/src/trainingDatasets/data/MNIST/train-labels.idx1-ubyte";

  static const std::string MNIST_BENCHMARK_IMAGES_PATH = "/home/aidan/workspace/ai-dan-cpp/src/trainingDatasets/data/MNIST/t10k-images.idx3-ubyte";
  static const std::string MNIST_BENCHMARK_LABELS_PATH = "/home/aidan/workspace/ai-dan-cpp/src/trainingDatasets/data/MNIST/t10k-labels.idx1-ubyte";

  // Back-prop consts 
  static const double training_dataset_min_cost = 0.0001;
  static const long long max_iterations = 1'000'000'000;
  static const double LEARNING_RATE = 0.001;
  static const double gradient_clip = 5.0;
  static const double LEARNING_RATE_ADJUST = 1.0; // Prevents overfitting if needed

  static const double momentum_coefficient = 0.9;
  static const double momentum_coefficient_variance = 0.999;

  // MNIST
  static const size_t MNIST_BATCH_SIZE = 32;

  // Threading thresholds
  static const size_t MIN_NEURONS_FOR_THREADING = 128;  // Don't parallelize tiny layers
  static const size_t MIN_WORK_PER_THREAD = 32;         // Minimum neurons per thread
}

namespace ThreadingUtils {
  // Helper to determine if a layer should use threading
  inline bool shouldUseThreading(size_t layer_size) {
    return layer_size >= Constants::MIN_NEURONS_FOR_THREADING;
  }

  // Calculate optimal thread count for a given workload
  inline size_t getOptimalThreadCount(size_t work_items) {
    if (work_items < Constants::MIN_NEURONS_FOR_THREADING) {
      return 1;  // Serial execution
    }

    const size_t max_threads = std::thread::hardware_concurrency();
    const size_t optimal_threads = work_items / Constants::MIN_WORK_PER_THREAD;

    return std::max(size_t(1), std::min(optimal_threads, max_threads));
  }
}

#endif // CONSTANTS_HPP

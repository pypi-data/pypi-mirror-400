#include "components/network.hpp"
#include "components/optimizer.hpp"
#include "components/trainer.hpp"
#include "components/benchmarker.hpp"
#include "training/datasets/MNIST.hpp"
#include "training/datasets/MNIST-benchmark.hpp"
#include "helpers/log.hpp"
#include "helpers/ArgsHelper.hpp"
#include "helpers/formatting.hpp"
#include "helpers/ModelSerializer.hpp"
#include <cstring>
#include <cmath>

void visualize_element(const DatasetElement& element, 
                       std::span<double> output) {
    const size_t rows = static_cast<size_t>(std::sqrt(element.input.size()));
    const size_t cols = rows;
    Logger::log("Printing MNIST input | rows: {}, cols: {}", rows, cols);
    for (uint16_t i = 0; i < rows; i++) {
      Logger::p("\t");
      for (uint16_t j = 0; j < cols; j++) {
        const double pixel = element.input[i * rows + j];
        Logger::p(Formatting::getGradientFromValue(pixel));
      }
      Logger::p("\n");
    }

    Logger::log("Expected Output: ", 0);
    Formatting::printProbabilityDistribution(element.label);

    Logger::log("Network Output: ", 0);
    Formatting::printProbabilityDistribution(output);
}

const std::function<void(size_t, double, const DatasetElement&, std::span<double>)> log_epoch
  = [](size_t step, double loss_val, 
      const DatasetElement& element, std::span<double> output) {
    Logger::log("Step: {}\tLoss: {:.2f}", step, loss_val);
    visualize_element(element, output);
  };

const std::function<void(const DatasetElement&, std::span<double>)> incorrect_callback
  = [](const DatasetElement& element, std::span<double> output) {
    Logger::log("Incorrect");
    visualize_element(element, output);
  };

void train(const ArgsConfig& args) {
  Logger::log("Training");

  // Dataset
  MNIST mnist;

  // Network
  Network network({784, 256, 128, 10}, 
                  Activations::ActivationEnum::kRelu,
                  Activations::ActivationEnum::kSoftmax);

  // Hyperparameters
  Optimizer optimizer(Constants::LEARNING_RATE, 
                      Constants::MNIST_BATCH_SIZE);

  // Trainer class
  const std::shared_ptr<Losses::Loss> loss = 
    std::make_shared<Losses::CrossEntropy>();
  Trainer trainer(network, 
                  optimizer, 
                  loss,
                  log_epoch);

  // Train
  trainer.train(mnist);

  if (!args.output_path.empty()) {
    ModelSerializer::save(network, args.output_path);
  }
}

void benchmark(const ArgsConfig& args) {
  Logger::log("Benchmark");

  // Dataset
  MNISTBenchmark mnist_benchmark;

  // network
  Network network = ModelSerializer::load(args.input_path);

  // Benchmarker class
  Benchmarker benchmarker(network, mnist_benchmark, incorrect_callback);

  // Benchmark
  benchmarker.benchmark();
}

int main(const int argc, const char* argv[]) {
  const ArgsConfig args(argc, argv);

  Logger::log("Train: {}\tBenchmark: {}", args.train, args.benchmark);
  Logger::log("Input: {}\tOutput: {}", args.input_path, args.output_path);

  if (args.train) {
    Logger::log("Training");
    train(args);
  }

  if (args.benchmark) {
    Logger::log("Benchmarking");
    benchmark(args);
  }
}

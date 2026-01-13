#include "components/benchmarker.hpp"
#include "helpers/profiler.hpp"

void Benchmarker::benchmark() {
  size_t iteration = 0;
  size_t incorrect = 0;

  for (; !dataset_.outOfElements(); iteration++) {
    const std::string step = std::format("{:5}", iteration);
    Profiler profile("Benchmark loop: " + step);

    const DatasetElement element = dataset_.getNextElement();
    network_.forward(element.input);

    const std::span<double>& output_layer = network_.getOutput();
    if (!dataset_.isOutputCorrect(output_layer, element.label)) {
      incorrect_callback_(element, output_layer);
      incorrect++;
    }
  }

  const double hitPercentage = 1.0 - static_cast<double>(incorrect) / static_cast<double>(iteration);
  Logger::log("Completed. Iterations: {}\tIncorrect: {}\tHit-Percentage: {:2f}",
      iteration, incorrect, hitPercentage);
}

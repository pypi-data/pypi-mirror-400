#ifndef BENCHMARKER_HPP
#define BENCHMARKER_HPP

#include "components/network.hpp"

class Benchmarker {
public:
  Benchmarker(Network& network,
              Dataset& dataset,
              const std::function<void(const DatasetElement& element,
                                       std::span<double>)> incorrect_callback)
    : network_(network),
      dataset_(dataset),
      incorrect_callback_(incorrect_callback) {}

  void benchmark();

private:
  Network& network_;
  Dataset& dataset_;
  const std::function<void(const DatasetElement& element,
                           std::span<double> model_output)> incorrect_callback_;
};

#endif // BENCHMARK_HPP

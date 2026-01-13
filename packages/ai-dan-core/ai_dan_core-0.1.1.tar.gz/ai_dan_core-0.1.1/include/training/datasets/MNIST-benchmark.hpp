#ifndef MNIST_BENCHMARK_HPP
#define MNIST_BENCHMARK_HPP

#include "training/dataset.hpp"
#include <cstdint>
#include <vector>
#include <fstream>

class MNISTBenchmark : public Dataset {
public:
    explicit MNISTBenchmark();
    ~MNISTBenchmark() override = default;

    DatasetElement getNextElement() override;
    DatasetElement getElement(const size_t index) override;
    bool isOutputCorrect(std::span<double> label, 
                         std::span<double> computed) const override;

    size_t rows;
    size_t cols;
private:
    std::vector<size_t> network_structure_ = {784, 256, 128, 10};

    EntryCountAndSize populateVectorFromIdx3(const std::string& file_path, std::vector<double>& vec);
    EntryCountAndSize populateVectorFromIdx1(const std::string& file_path, std::vector<double>& vec);

    uint32_t readBigEndianInt(std::ifstream& f);
};

#endif // MNIST_BENCHMARK_HPP

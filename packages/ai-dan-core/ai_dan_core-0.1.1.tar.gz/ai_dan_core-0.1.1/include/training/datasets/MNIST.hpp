#ifndef MNIST_HPP
#define MNIST_HPP

#include "training/dataset.hpp"
#include <cstdint>
#include <vector>
#include <fstream>

class MNIST : public Dataset {
public:
    explicit MNIST();
    ~MNIST() override = default;

    DatasetElement getNextElement() override;
    DatasetElement getElement(const size_t index) override;
    bool isOutputCorrect(std::span<double> label, 
                         std::span<double> computed) const override;

    size_t rows;
    size_t cols;
private:
    EntryCountAndSize populateVectorFromIdx3(const std::string& file_path, 
                                             std::vector<double>& vec);
    EntryCountAndSize populateVectorFromIdx1(const std::string& file_path, 
                                             std::vector<double>& vec);

    uint32_t readBigEndianInt(std::ifstream& f);
};

#endif

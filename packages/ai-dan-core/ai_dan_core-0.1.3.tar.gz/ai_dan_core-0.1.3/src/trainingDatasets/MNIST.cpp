#include "training/datasets/MNIST.hpp"
#include "helpers/log.hpp"
#include "helpers/constants.hpp"
#include "helpers/exceptions.hpp"
#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <algorithm>

MNIST::MNIST() {
    EntryCountAndSize training = populateVectorFromIdx3(
        Constants::MNIST_TRAINING_IMAGES_PATH, inputs_);
    inputs_count_ = training.entry_count;
    inputs_size_ = training.entry_size;

    EntryCountAndSize labels = populateVectorFromIdx1(
        Constants::MNIST_TRAINING_LABELS_PATH, labels_);
    labels_count_ = labels.entry_count;
    labels_size_ = labels.entry_size;
}
               
DatasetElement MNIST::getNextElement() {
  return getElement(iteration_++);
}

DatasetElement MNIST::getElement(const size_t index) {
  return DatasetElement {
    std::span(inputs_.data() + index * inputs_size_, inputs_size_), 
    std::span(labels_.data() + index * labels_size_, labels_size_)
  };
}

bool MNIST::isOutputCorrect(std::span<double> label, std::span<double> computed) const {
  const int label_index = getNumericalOutput(label);
  const int computed_index = getNumericalOutput(computed);
  return label_index == computed_index;
}

uint32_t MNIST::readBigEndianInt(std::ifstream& f) {
    unsigned char bytes[4];
    f.read(reinterpret_cast<char*>(bytes), 4);
    return (uint32_t(bytes[0]) << 24) | 
           (uint32_t(bytes[1]) << 16) |
           (uint32_t(bytes[2]) << 8) |
           (uint32_t(bytes[3]));
}


EntryCountAndSize MNIST::populateVectorFromIdx3(const std::string& file_path, std::vector<double>& vec) {
    std::ifstream file(file_path, std::ios::binary);

    if (!file.is_open()) {
        throw NeuralNet::FileLoadError("Failed to open file: " + file_path);
    }

    uint32_t magic = readBigEndianInt(file);
    if (magic != 2051) {
        throw NeuralNet::DatasetError(
            "Invalid IDX3 file format: expected magic number 2051, got " + std::to_string(magic)
        );
    }

    uint32_t input_count = readBigEndianInt(file);
    rows = readBigEndianInt(file);
    cols = readBigEndianInt(file);
    uint32_t inputs_size = rows * cols * input_count;

    Logger::log("Inputs: {}, Rows: {}, Cols: {}, Input Vector Size: {}", 
        input_count, rows, cols, inputs_size_);

    vec.resize(inputs_size);
    std::vector<uint8_t> images(inputs_size);
    file.read(reinterpret_cast<char*>(images.data()), inputs_size);
    std::transform(images.begin(), images.end(), vec.begin(), 
      [](uint8_t val) {
        return (static_cast<double>(val) / 255); 
      });

    file.close();

    return { input_count, static_cast<size_t>(rows * cols)};
}

EntryCountAndSize MNIST::populateVectorFromIdx1(const std::string& file_path, std::vector<double>& vec) {
    std::ifstream file(file_path, std::ios::binary);
    if (!file.is_open()) {
        throw NeuralNet::FileLoadError("Failed to open file: " + file_path);
    }

    uint32_t magic = readBigEndianInt(file);
    if (magic != 2049) {
        throw NeuralNet::DatasetError(
            "Invalid IDX1 file format: expected magic number 2049, got " + std::to_string(magic)
        );
    }
    uint32_t entry_count = readBigEndianInt(file);

    std::vector<uint8_t> labels(entry_count);
    file.read(reinterpret_cast<char*>(labels.data()), entry_count);
    vec.resize(entry_count * 10);

    for (size_t i = 0; i < entry_count; i++) {
      vec[i * 10 + labels[i]] = 1.0;
    }

    file.close();

    return { entry_count, 10 };
}

#ifndef TRAINING_DATASET_HPP
#define TRAINING_DATASET_HPP

#include <cassert>
#include <vector>

class Network;
class TrainingArtifacts;

#include <span>

struct DatasetElement {
    std::span<double> input;
    std::span<double> label;
};

struct EntryCountAndSize {
  size_t entry_count;
  size_t entry_size;
};

struct Dataset {
    virtual DatasetElement getNextElement() = 0;
    virtual bool isOutputCorrect(std::span<double> label, std::span<double> computed) const = 0;
    virtual DatasetElement getElement(const size_t index) = 0;
    virtual bool outOfElements() const {
      return iteration_ >= inputs_count_;
    }

    virtual ~Dataset() = default;

protected:
    explicit Dataset() : inputs_(), labels_() {}

    size_t iteration_ = 0;

    std::vector<double> inputs_;
    std::vector<double> labels_;

    size_t inputs_count_;
    size_t inputs_size_;

    size_t labels_count_;
    size_t labels_size_;

    inline size_t getNumericalOutput(const std::span<double>& input) const {
      int index = 0;
      double max = input[index];
      for (int i = index; i < input.size(); i++) {
        if (input[i] > max) {
          max = input[i];
          index = i;
        }
      }
      return index;
    }
};

#endif

#ifndef LOSS_HPP 
#define LOSS_HPP

#include "helpers/threadPool.hpp"
#include "helpers/activations.hpp"
#include <map>
#include <span>
#include <assert.h>

namespace Losses {
  enum class LossEnum : uint8_t { kMeanSquaredError, kCrossEntropy };

  class Loss {
  public:
    virtual double loss(const Layer* output_layer, 
                        ThreadPool& thread_pool, 
                        const std::span<double> target) const = 0;
    virtual void delta(const Layer* output_layer, 
                       ThreadPool& thread_pool, 
                       const std::span<double> target, 
                       const std::shared_ptr<Activations::Activation> activation) const = 0;
    virtual const Losses::LossEnum getLossValue() const = 0;
  };

  class MeanSquaredError : public Loss {
  public:
    MeanSquaredError() = default;

    double loss(const Layer* output_layer, 
                ThreadPool& thread_pool, 
                const std::span<double> target) const override;
    void delta(const Layer* output_layer, 
               ThreadPool& thread_pool, 
               const std::span<double> target, 
               const std::shared_ptr<Activations::Activation> activation) const override;
    const Losses::LossEnum getLossValue() const override {
      return Losses::LossEnum::kMeanSquaredError;
    }
  };

  class CrossEntropy : public Loss {
  public:
    CrossEntropy() = default;

    double loss(const Layer* output_layer, 
                ThreadPool& thread_pool, 
                const std::span<double> target) const override;
    void delta(const Layer* output_layer, 
               ThreadPool& thread_pool, 
               const std::span<double> target, 
               const std::shared_ptr<Activations::Activation> activation) const override;
    const Losses::LossEnum getLossValue() const override {
      return Losses::LossEnum::kCrossEntropy;
    }
  };

  extern const std::map<Losses::LossEnum, std::shared_ptr<Losses::Loss>> lossMap;
}

#endif

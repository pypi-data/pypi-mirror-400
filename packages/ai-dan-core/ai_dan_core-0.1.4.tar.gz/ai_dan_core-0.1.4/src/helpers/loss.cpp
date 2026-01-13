#include "helpers/activations.hpp"
#include "helpers/loss.hpp"
#include "components/layer.hpp"
#include <cmath>
#include <latch>

// MSE Loss
double Losses::MeanSquaredError::loss(const Layer* output_layer,
                                      ThreadPool& thread_pool,
                                      const std::span<double> target) const {
    double sum = 0.0;
    for (size_t i = 0; i < output_layer->getSize(); ++i) {
        double diff = output_layer->getValue(i) - target[i];
        sum += diff * diff;
    }
    return 0.5 * sum;
}

// MSE Delta
void Losses::MeanSquaredError::delta(const Layer* output_layer,
                                     ThreadPool& thread_pool,
                                     const std::span<double> target,
                                     const std::shared_ptr<Activations::Activation> activation_bundle) const {
  std::latch done(output_layer->getSize());
  std::span<double> deltas = output_layer->getDeltas();

  for (size_t i = 0; i < output_layer->getSize(); ++i) {
    thread_pool.enqueue([&, i] () {
      double a = output_layer->getValue(i);
      double z = output_layer->getPreActivatedValue(i);
      double diff = a - target[i];
      deltas[i] = diff * activation_bundle->derive(z, a);
      done.count_down();
    });
  }

  done.wait();
}

// Cross-Entropy Loss
double Losses::CrossEntropy::loss(const Layer* output_layer,
                                  ThreadPool& thread_pool,
                                  const std::span<double> target) const {
    double sum = 0.0;
    for (size_t i = 0; i < output_layer->getSize(); ++i) {
        double a = output_layer->getValue(i);
        sum += -target[i] * std::log(a + 1e-12);
    }
    return sum;
}

// Cross-Entropy Delta
void Losses::CrossEntropy::delta(const Layer* output_layer,
                                 ThreadPool& thread_pool,
                                 const std::span<double> target,
                                 const std::shared_ptr<Activations::Activation> activation_bundle) const {
    std::span<double> deltas = output_layer->getDeltas();

    switch (activation_bundle->getActivationValue()) {
        case Activations::ActivationEnum::kSigmoid:
        case Activations::ActivationEnum::kSoftmax:
          {
            std::latch done(output_layer->getSize());
            // Optimized formula for sigmoid+CE or softmax+CE: delta = a - y
            for (size_t i = 0; i < output_layer->getSize(); ++i) {
              thread_pool.enqueue([&, i] () {
                deltas[i] = output_layer->getValue(i) - target[i];
                done.count_down();
              });
            }

            done.wait();
            break;
          }
        default:
          {
            std::latch done(output_layer->getSize());
            // General fallback: delta = dL/da * f'(z)
            for (size_t i = 0; i < output_layer->getSize(); ++i) {
              thread_pool.enqueue([&, i] () {
                double a = output_layer->getValue(i);
                double z = output_layer->getPreActivatedValue(i);
                double dL_da = (-target[i] / (a + 1e-12)) + ((1.0 - target[i]) / (1.0 - a + 1e-12));
                deltas[i] = dL_da * activation_bundle->derive(z, a);
              });
            }

            done.wait();
            break;
          }
    }
}

const std::map<Losses::LossEnum, std::shared_ptr<Losses::Loss>> Losses::lossMap = {
  { Losses::LossEnum::kMeanSquaredError, std::make_shared<MeanSquaredError>() },
  { Losses::LossEnum::kCrossEntropy, std::make_shared<CrossEntropy>() },
};

#ifndef ACTIVATIONS_HPP
#define ACTIVATIONS_HPP

#include "helpers/threadPool.hpp"
#include "helpers/math.hpp"
#include <map>
#include <assert.h>

class Network;
class Layer;

namespace Activations {
  enum class ActivationEnum : uint8_t { kRelu, kLeakyRelu, kSigmoid, kTanh, kSoftmax };

  class Activation {
  public:
    virtual void activate(Layer&, ThreadPool&) const = 0;
    virtual double derive(const double, const double) const = 0;
    virtual double initializeWeights(const Network&, const Layer&) const = 0;
    virtual Activations::ActivationEnum getActivationValue() const = 0;
  protected:
    Activation() = default;
    ~Activation() = default;
  };
  
  class Relu : public Activation {
  public:
    Relu() = default;

    void activate(Layer& layer, ThreadPool& thread_pool) const override {
      return Math::relu_layer(layer, thread_pool);
    }
    double derive(const double pre_activated_value, const double activated_value) const override {
      return Math::relu_derivative(pre_activated_value, activated_value);
    }
    double initializeWeights(const Network& network, const Layer& layer) const override {
      return Math::he_init_initialization(network, layer);
    }
    Activations::ActivationEnum getActivationValue() const override { 
      return Activations::ActivationEnum::kRelu; 
    }
  };
  
  class LeakyRelu : public Activation {
  public:
    LeakyRelu() = default;

    void activate(Layer& layer, ThreadPool& thread_pool) const override {
      return Math::leaky_relu_layer(layer, thread_pool);
    }
    double derive(const double pre_activated_value, const double activated_value) const override {
      return Math::leak_relu_derivative(pre_activated_value, activated_value);
    }
    double initializeWeights(const Network& network, const Layer& layer) const override {
      return Math::he_init_initialization(network, layer);
    }
    Activations::ActivationEnum getActivationValue() const override { 
      return Activations::ActivationEnum::kLeakyRelu; 
    }
  };

  class Sigmoid : public Activation {
  public:
    Sigmoid() = default;

    void activate(Layer& layer, ThreadPool& thread_pool) const override {
      return Math::sigmoid_layer(layer, thread_pool);
    }
    double derive(const double pre_activated_value, const double activated_value) const override {
      return Math::sigmoid_derivative(pre_activated_value, activated_value);
    }
    double initializeWeights(const Network& network, const Layer& layer) const override {
      return Math::xavier_initialization(network, layer);
    }
    Activations::ActivationEnum getActivationValue() const override { 
      return Activations::ActivationEnum::kSigmoid; 
    }
  };

  class Tanh : public Activation {
  public:
    Tanh() = default;

    void activate(Layer& layer, ThreadPool& thread_pool) const override {
      return Math::tanh_layer(layer, thread_pool);
    }
    double derive(const double pre_activated_value, const double activated_value) const override {
      return Math::tanh_derivative(pre_activated_value, activated_value);
    }
    double initializeWeights(const Network& network, const Layer& layer) const override {
      return Math::xavier_initialization(network, layer);
    }
    Activations::ActivationEnum getActivationValue() const override { 
      return Activations::ActivationEnum::kTanh; 
    }
  private:
  };

  class Softmax : public Activation {
  public:
    Softmax() = default;

    void activate(Layer& layer, ThreadPool& thread_pool) const override {
      return Math::softmax_layer(layer, thread_pool);
    }
    double derive(const double pre_activated_value, const double activated_value) const override {
      return Math::softmax_derivative(pre_activated_value, activated_value);
    }
    double initializeWeights(const Network& network, const Layer& layer) const override {
      return Math::xavier_initialization(network, layer);
    }
    Activations::ActivationEnum getActivationValue() const override { 
      return Activations::ActivationEnum::kSoftmax; 
    }
  };

  extern const std::map<ActivationEnum, const std::shared_ptr<Activation>> activationMap;
}

#endif

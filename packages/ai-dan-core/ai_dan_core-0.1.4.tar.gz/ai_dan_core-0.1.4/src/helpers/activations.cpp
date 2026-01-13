#include "helpers/activations.hpp"

const std::map<Activations::ActivationEnum, const std::shared_ptr<Activations::Activation>> Activations::activationMap = {
  { Activations::ActivationEnum::kRelu, std::make_shared<Relu>() },
  { Activations::ActivationEnum::kLeakyRelu, std::make_shared<LeakyRelu>() },
  { Activations::ActivationEnum::kSigmoid, std::make_shared<Sigmoid>() },
  { Activations::ActivationEnum::kTanh, std::make_shared<Tanh>() },
  { Activations::ActivationEnum::kSoftmax, std::make_shared<Softmax>() },
};

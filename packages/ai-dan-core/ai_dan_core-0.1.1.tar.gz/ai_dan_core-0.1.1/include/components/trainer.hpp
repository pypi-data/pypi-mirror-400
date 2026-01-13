#ifndef TRAINER_HPP
#define TRAINER_HPP

#include <functional>
#include "components/network.hpp"
#include "components/optimizer.hpp"

class Trainer {
public:
  Trainer(Network& network,
          Optimizer& optimizer,
          const std::shared_ptr<Losses::Loss> loss,
          const std::function<void(size_t,
                                   double,
                                   const DatasetElement&,
                                   std::span<double>)> epoch_callback)
    : network_(network),
      optimizer_(optimizer),
      loss_(loss),
      epoch_callback_(epoch_callback) {}

  void train(Dataset& dataset);

private:
  Network& network_;
  Optimizer& optimizer_;
  const std::shared_ptr<Losses::Loss> loss_;
  const std::function<void(size_t,
                           double,
                           const DatasetElement&,
                           std::span<double>)> epoch_callback_;
};

#endif // TRAINER_HPP

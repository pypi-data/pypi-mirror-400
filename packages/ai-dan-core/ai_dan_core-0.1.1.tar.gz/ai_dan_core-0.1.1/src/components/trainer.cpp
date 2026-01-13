#include "components/trainer.hpp"

void Trainer::train(Dataset& dataset) {
  size_t step = 0;
  double accumulated_loss = 0.0;

  while (!dataset.outOfElements()) {
    const DatasetElement element = dataset.getNextElement();

    network_.forward(element.input);
    network_.backward(element.label, loss_);

    const Layer& output_layer = network_.getLayers().at(network_.getLayers().size() - 1);
    accumulated_loss += loss_->loss(&output_layer, ThreadPool::global(), element.label);
    step++;

    if (step % optimizer_.getBatchSize() == 0) {
      optimizer_.step(network_);

      epoch_callback_(step, 
                      accumulated_loss / optimizer_.getBatchSize(), 
                      element, 
                      network_.getOutput());
      accumulated_loss = 0.0;
    }
  }
}


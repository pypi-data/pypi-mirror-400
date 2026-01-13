# ai-dan-core

High-performance neural network library with C++ backend and Python bindings.

## Features

- **Fast C++ backend** with adaptive multi-threading
- **Simple Python API** for easy integration
- **Built-in MNIST support** for quick experimentation
- **Flexible architecture** supporting multiple activation functions and loss functions
- **Model persistence** - save and load trained models

## Installation

```bash
pip install ai-dan-core
```

## Quick Start

```python
import ai_dan

# Create a neural network
network = ai_dan.Network([784, 256, 128, 10],
                         ai_dan.LEAKY_RELU,
                         ai_dan.SOFTMAX)

# Configure training
optimizer = ai_dan.Optimizer(learning_rate=0.001, batch_size=32)
loss = ai_dan.CrossEntropy()

# Train on MNIST
trainer = ai_dan.Trainer(network, optimizer, loss)
trainer.train(ai_dan.MNIST())

# Save the model
network.save("model.ai-dan")

# Load and benchmark
loaded = ai_dan.Network.load("model.ai-dan")
benchmarker = ai_dan.Benchmarker(loaded, ai_dan.MNISTBenchmark())
benchmarker.benchmark()
```

## Activation Functions

- `ai_dan.SIGMOID`
- `ai_dan.RELU`
- `ai_dan.LEAKY_RELU`
- `ai_dan.TANH`
- `ai_dan.SOFTMAX`

## Loss Functions

- `ai_dan.MSE` (Mean Squared Error)
- `ai_dan.CROSS_ENTROPY`

## Training with Callbacks

Monitor training progress with custom callbacks:

```python
def on_step(step, loss_val, input_vec, label_vec, output_vec):
    if step % 1000 == 0:
        print(f"Step {step}, Loss: {loss_val:.4f}")

trainer = ai_dan.Trainer(network, optimizer, loss, on_step)
trainer.train(mnist_data)
```

## Performance

- Training on MNIST: ~20 seconds for 60,000 samples
- Throughput: ~3,000 samples/second
- Typical accuracy: 96%+ on MNIST test set

## Requirements

- Python 3.8+
- C++23 compatible compiler (GCC 13+, Clang 16+)

## License

MIT

#!/usr/bin/env python3
import sys
sys.path.insert(0, 'build')
import ai_dan
import time

# Create network and optimizer
batch_size = 32
network = ai_dan.Network([784, 256, 128, 10],
                         ai_dan.LEAKY_RELU,
                         ai_dan.SOFTMAX)
optimizer = ai_dan.Optimizer(0.001, batch_size)
loss = ai_dan.CrossEntropy()

# Train with callback
print("Training...")
mnist_train = ai_dan.MNIST()

def on_step(step, loss_val, input_vec, label_vec, output_vec):
    if (step % (batch_size * 100) == 0):
        print(f"  Step {step}, Loss: {loss_val:.4f}")

trainer = ai_dan.Trainer(network, optimizer, loss, on_step)
start = time.time()
trainer.train(mnist_train)
print(f"Training: {time.time() - start:.1f}s")

# Save and load
network.save("./models/temp.ai-dan")
loaded = ai_dan.Network.load("./models/temp.ai-dan")

# Benchmark
mnist_test = ai_dan.MNISTBenchmark()
errors = [0]
def count_error(i, l, o):
    errors[0] += 1

benchmarker = ai_dan.Benchmarker(loaded, mnist_test, count_error)
start = time.time()
benchmarker.benchmark()
print(f"Benchmark: {time.time() - start:.1f}s, Accuracy: {(10000-errors[0])/100:.1f}%")

// Python bindings for ai-dan neural network library
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

#include "components/network.hpp"
#include "components/optimizer.hpp"
#include "components/trainer.hpp"
#include "components/benchmarker.hpp"
#include "helpers/activations.hpp"
#include "helpers/loss.hpp"
#include "helpers/exceptions.hpp"
#include "helpers/ModelSerializer.hpp"
#include "training/dataset.hpp"
#include "training/datasets/MNIST.hpp"
#include "training/datasets/MNIST-benchmark.hpp"

namespace py = pybind11;

// Wrapper for Trainer to handle Python callbacks with proper GIL management
class TrainerPython {
public:
    TrainerPython(Network& network,
                  Optimizer& optimizer,
                  std::shared_ptr<Losses::Loss> loss,
                  py::object callback = py::none())
        : network_(network)
        , optimizer_(optimizer)
        , loss_(loss)
        , py_callback_(callback) {}

    void train(Dataset& dataset) {
        auto cpp_callback = [this](size_t step,
                                   double loss_val,
                                   const DatasetElement& elem,
                                   std::span<double> output) {
            if (!py_callback_.is_none()) {
                py::gil_scoped_acquire acquire;
                try {
                    std::vector<double> output_vec(output.begin(), output.end());
                    std::vector<double> input_vec(elem.input.begin(), elem.input.end());
                    std::vector<double> label_vec(elem.label.begin(), elem.label.end());
                    py_callback_(step, loss_val, input_vec, label_vec, output_vec);
                } catch (const py::error_already_set& e) {
                    py::print("Python callback error:", e.what());
                }
            }
        };

        Trainer trainer(network_, optimizer_, loss_, cpp_callback);
        trainer.train(dataset);
    }

private:
    Network& network_;
    Optimizer& optimizer_;
    std::shared_ptr<Losses::Loss> loss_;
    py::object py_callback_;
};

// Wrapper for Benchmarker
class BenchmarkerPython {
public:
    BenchmarkerPython(Network& network,
                      Dataset& dataset,
                      py::object callback = py::none())
        : network_(network)
        , dataset_(dataset)
        , py_callback_(callback) {}

    void benchmark() {
        auto cpp_callback = [this](const DatasetElement& elem,
                                   std::span<double> output) {
            if (!py_callback_.is_none()) {
                py::gil_scoped_acquire acquire;
                try {
                    std::vector<double> output_vec(output.begin(), output.end());
                    std::vector<double> input_vec(elem.input.begin(), elem.input.end());
                    std::vector<double> label_vec(elem.label.begin(), elem.label.end());
                    py_callback_(input_vec, label_vec, output_vec);
                } catch (const py::error_already_set& e) {
                    py::print("Python callback error:", e.what());
                }
            }
        };

        Benchmarker benchmarker(network_, dataset_, cpp_callback);
        benchmarker.benchmark();
    }

private:
    Network& network_;
    Dataset& dataset_;
    py::object py_callback_;
};

PYBIND11_MODULE(ai_dan, m) {
    m.doc() = "High-performance neural network library with C++ backend";

    // ===== Exceptions =====
    py::register_exception<NeuralNet::NetworkException>(m, "NetworkException");
    py::register_exception<NeuralNet::InvalidInputError>(m, "InvalidInputError");
    py::register_exception<NeuralNet::InvalidTargetError>(m, "InvalidTargetError");
    py::register_exception<NeuralNet::LayerConfigurationError>(m, "LayerConfigurationError");
    py::register_exception<NeuralNet::FileLoadError>(m, "FileLoadError");
    py::register_exception<NeuralNet::DatasetError>(m, "DatasetError");
    py::register_exception<NeuralNet::BufferError>(m, "BufferError");
    py::register_exception<NeuralNet::NotImplementedError>(m, "NotImplementedError");
    py::register_exception<NeuralNet::OptimizerError>(m, "OptimizerError");

    // ===== Activation functions (expose as module-level constants) =====
    m.attr("SIGMOID") = static_cast<int>(Activations::ActivationEnum::kSigmoid);
    m.attr("RELU") = static_cast<int>(Activations::ActivationEnum::kRelu);
    m.attr("LEAKY_RELU") = static_cast<int>(Activations::ActivationEnum::kLeakyRelu);
    m.attr("TANH") = static_cast<int>(Activations::ActivationEnum::kTanh);
    m.attr("SOFTMAX") = static_cast<int>(Activations::ActivationEnum::kSoftmax);

    m.attr("MSE") = static_cast<int>(Losses::LossEnum::kMeanSquaredError);
    m.attr("CROSS_ENTROPY") = static_cast<int>(Losses::LossEnum::kCrossEntropy);

    // ===== Loss Classes =====
    py::class_<Losses::Loss, std::shared_ptr<Losses::Loss>>(m, "LossBase");

    py::class_<Losses::MeanSquaredError, Losses::Loss, std::shared_ptr<Losses::MeanSquaredError>>(m, "MeanSquaredError")
        .def(py::init<>(), "Mean Squared Error loss function");

    py::class_<Losses::CrossEntropy, Losses::Loss, std::shared_ptr<Losses::CrossEntropy>>(m, "CrossEntropy")
        .def(py::init<>(), "Cross Entropy loss function");

    // ===== Network =====
    py::class_<Network>(m, "Network")
        .def(py::init([](const std::vector<uint64_t>& layers, int hidden_act, int output_act) {
                 return new Network(layers,
                                   static_cast<Activations::ActivationEnum>(hidden_act),
                                   static_cast<Activations::ActivationEnum>(output_act));
             }),
             py::arg("layers"),
             py::arg("hidden_activation"),
             py::arg("output_activation"),
             "Create a neural network\n\n"
             "Args:\n"
             "    layers: List of layer sizes [input, hidden1, hidden2, ..., output]\n"
             "    hidden_activation: Activation function for hidden layers (use RELU, SIGMOID, etc.)\n"
             "    output_activation: Activation function for output layer")

        .def("forward",
             [](Network& self, const std::vector<double>& input) {
                 std::vector<double> input_copy = input;
                 self.forward(input_copy);
             },
             py::call_guard<py::gil_scoped_release>(),
             py::arg("input"),
             "Perform forward propagation")

        .def("get_output",
             [](const Network& self) {
                 std::span<double> output = self.getOutput();
                 return std::vector<double>(output.begin(), output.end());
             },
             "Get the output of the network after forward pass")

        .def("save",
             [](const Network& self, const std::string& path) {
                 ModelSerializer::save(self, path);
             },
             py::arg("path"),
             "Save the network to a file")

        .def_static("load",
             [](const std::string& path) {
                 return ModelSerializer::load(path);
             },
             py::arg("path"),
             "Load a network from a file");

    // ===== Optimizer =====
    py::class_<Optimizer>(m, "Optimizer")
        .def(py::init<double, size_t>(),
             py::arg("learning_rate"),
             py::arg("batch_size"),
             "Create an optimizer\n\n"
             "Args:\n"
             "    learning_rate: Learning rate (must be > 0)\n"
             "    batch_size: Batch size (must be > 0)")

        .def("get_learning_rate", &Optimizer::getLearningRate, "Get the learning rate")
        .def("get_batch_size", &Optimizer::getBatchSize, "Get the batch size");

    // ===== Dataset (abstract base) =====
    py::class_<Dataset>(m, "Dataset");

    // ===== MNIST Datasets =====
    py::class_<MNIST, Dataset>(m, "MNIST")
        .def(py::init<>(), "Load MNIST training dataset (60,000 samples)");

    py::class_<MNISTBenchmark, Dataset>(m, "MNISTBenchmark")
        .def(py::init<>(), "Load MNIST test dataset (10,000 samples)");

    // ===== Trainer =====
    py::class_<TrainerPython>(m, "Trainer")
        .def(py::init<Network&, Optimizer&, std::shared_ptr<Losses::Loss>, py::object>(),
             py::keep_alive<1, 2>(),
             py::keep_alive<1, 3>(),
             py::arg("network"),
             py::arg("optimizer"),
             py::arg("loss"),
             py::arg("callback") = py::none(),
             "Create a trainer\n\n"
             "Args:\n"
             "    network: The neural network to train\n"
             "    optimizer: The optimizer to use\n"
             "    loss: The loss function to use\n"
             "    callback: Optional callback function(step, loss, input, label, output)")

        .def("train",
             &TrainerPython::train,
             py::call_guard<py::gil_scoped_release>(),
             py::arg("dataset"),
             "Train the network on the given dataset");

    // ===== Benchmarker =====
    py::class_<BenchmarkerPython>(m, "Benchmarker")
        .def(py::init<Network&, Dataset&, py::object>(),
             py::keep_alive<1, 2>(),
             py::keep_alive<1, 3>(),
             py::arg("network"),
             py::arg("dataset"),
             py::arg("callback") = py::none(),
             "Create a benchmarker\n\n"
             "Args:\n"
             "    network: The neural network to benchmark\n"
             "    dataset: The dataset to use for benchmarking\n"
             "    callback: Optional callback for incorrect predictions(input, label, output)")

        .def("benchmark",
             &BenchmarkerPython::benchmark,
             py::call_guard<py::gil_scoped_release>(),
             "Run benchmark on the dataset");
}

#ifndef MATH_H
#define MATH_H

#include "helpers/threadPool.hpp"
#include <span>

class Network;
class Layer;

namespace Math {
    /** SIGMOID */
    void sigmoid_layer(Layer& layer, ThreadPool& thread_pool);
    double sigmoid(const double x);
    double sigmoid_derivative(const double, const double activated_output);

    /** RELU*/
    void relu_layer(Layer& layer, ThreadPool& thread_pool);
    double relu(const double x);
    double relu_derivative(const double pre_activated_output, const double);

    /** LEAKY RELU*/
    void leaky_relu_layer(Layer& layer, ThreadPool& thread_pool);
    double leaky_relu(const double x);
    double leak_relu_derivative(const double pre_activated_output, const double activated_output);

    /** TANH */
    void tanh_layer(Layer& layer, ThreadPool& thread_pool);
    double tanh(const double x);
    double tanh_derivative(const double, const double activated_output);

    /** SOFTMAX */
    void softmax_layer(Layer& layer, ThreadPool&);
    double softmax_derivative(const double, const double);

    /** WEIGHT INITIALIZATION */
    double xavier_initialization(const Network& network, const Layer& layer);
    double he_init_initialization(const Network&, const Layer& layer);

    /** RANDOM HELPERS */
    void get_random_vector(std::span<double> input_span, const size_t size);
    double average_span(std::span<double> input);
    double getStandardDeviation(std::span<double> input, const double mean);
    void normalize(std::span<double> input);
};

#endif

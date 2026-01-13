#ifndef EXCEPTIONS_HPP
#define EXCEPTIONS_HPP

#include <stdexcept>
#include <string>

namespace NeuralNet {

// Base exception for all neural network errors
class NetworkException : public std::runtime_error {
public:
    explicit NetworkException(const std::string& message)
        : std::runtime_error(message) {}
};

// Input validation errors
class InvalidInputError : public NetworkException {
public:
    explicit InvalidInputError(const std::string& message)
        : NetworkException("Invalid input: " + message) {}
};

// Target/label validation errors
class InvalidTargetError : public NetworkException {
public:
    explicit InvalidTargetError(const std::string& message)
        : NetworkException("Invalid target: " + message) {}
};

// Layer configuration errors
class LayerConfigurationError : public NetworkException {
public:
    explicit LayerConfigurationError(const std::string& message)
        : NetworkException("Layer configuration error: " + message) {}
};

// File I/O errors
class FileLoadError : public NetworkException {
public:
    explicit FileLoadError(const std::string& message)
        : NetworkException("File load error: " + message) {}
};

// Dataset errors
class DatasetError : public NetworkException {
public:
    explicit DatasetError(const std::string& message)
        : NetworkException("Dataset error: " + message) {}
};

// Buffer/memory errors
class BufferError : public NetworkException {
public:
    explicit BufferError(const std::string& message)
        : NetworkException("Buffer error: " + message) {}
};

// Not implemented features
class NotImplementedError : public NetworkException {
public:
    explicit NotImplementedError(const std::string& message)
        : NetworkException("Not implemented: " + message) {}
};

// Optimizer errors
class OptimizerError : public NetworkException {
public:
    explicit OptimizerError(const std::string& message)
        : NetworkException("Optimizer error: " + message) {}
};

} // namespace NeuralNet

#endif // EXCEPTIONS_HPP

#ifndef RANDOM_HPP
#define RANDOM_HPP

#include <random>

class Random {
public:
    // Returns a random double in the range [min, max)
    static double getDouble(double min, double max) {
        thread_local std::mt19937 engine{ std::random_device{}() };
        std::uniform_real_distribution<double> dist(min, max);
        return dist(engine);
    }

    static int getInt(int min, int max) {
        // Thread-local random engine ensures each thread has its own engine
        thread_local std::mt19937 engine{ std::random_device{}() };
        std::uniform_int_distribution<int> dist(min, max);
        return dist(engine);
    }
};

#endif
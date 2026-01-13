#ifndef PROFILER_HPP
#define PROFILER_HPP

#include "helpers/log.hpp"
#include <chrono>

class Profiler {
public:
  explicit Profiler(const std::string scope)
    : scope(scope),
    start(std::chrono::steady_clock::now()) {}

  ~Profiler() {
    auto end = std::chrono::steady_clock::now();

    std::chrono::nanoseconds ns   = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
    std::chrono::milliseconds ms  = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    std::chrono::seconds ss       = std::chrono::duration_cast<std::chrono::seconds>(end - start);

    Logger::debug("Scope: [{}] ellapsted Ns: {:9}\t Ms: {:5}\t Ss: {:2}", scope, ns, ms, ss);
  }

private:
  const std::string scope;
  const std::chrono::steady_clock::time_point start;
    

};

#endif // PROFILER_HPP

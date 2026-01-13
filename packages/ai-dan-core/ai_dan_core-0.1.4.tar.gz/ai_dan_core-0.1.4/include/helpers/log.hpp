#ifndef LOGGER_HPP
#define LOGGER_HPP

#include <format>
#include <string>
#include <mutex>
#include <iostream>
#include <sstream>
#include <thread>
#include "helpers/constants.hpp"

namespace Logger {
  inline std::mutex log_mutex;

  inline void p(const std::string log) {
    if (!Constants::log_enabled) return;
    if (Constants::log_level < Constants::LOG_LEVEL::DEBUG) { return; }
    std::cout << log;
  }

  // Thread unsafe logging
  template<typename... Args>
  inline void print_out(Constants::LOG_LEVEL level, std::format_string<Args...> format_str, Args&&... args) {
    std::string message = std::format(format_str, std::forward<Args>(args)...);
    std::ostringstream oss;
    oss << std::this_thread::get_id();
    std::string thread_id = oss.str();
    std::string level_str = Constants::LOG_LEVEL_STRING[level];

    std::cout << "[T " << thread_id << "] [" << level_str << "] " << message << std::endl;
  }

  template<typename... Args>
  inline void print(Constants::LOG_LEVEL level, std::format_string<Args...> format_str, Args&&... args) {
    if (!Constants::log_enabled) { return; }
    if (level < Constants::log_level) { return; }

    // Conditionally lock before logging or not
    if (Constants::lock_logging) { 
      std::scoped_lock lock(log_mutex);
      print_out(level, format_str, std::forward<Args>(args)...);
    } else {
      print_out(level, format_str, std::forward<Args>(args)...);
    }
  }

  template<typename... Args>
  inline void debug(std::format_string<Args...> format_str, Args&&... args) {
    print(Constants::LOG_LEVEL::DEBUG, format_str, std::forward<Args>(args)...);
  }

  template<typename... Args>
  inline void log(std::format_string<Args...> format_str, Args&&... args) {
    print(Constants::LOG_LEVEL::INFO, format_str, std::forward<Args>(args)...);
  }

  template<typename... Args>
  inline void err(std::format_string<Args...> format_str, Args&&... args) {
    print(Constants::LOG_LEVEL::ERROR, format_str, std::forward<Args>(args)...);
  }
}

#endif // LOGGER_HPP


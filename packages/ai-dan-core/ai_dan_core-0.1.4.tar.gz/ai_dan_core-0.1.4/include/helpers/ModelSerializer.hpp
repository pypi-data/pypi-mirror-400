#ifndef MODEL_SERIALIZER_HPP
#define MODEL_SERIALIZER_HPP

#include "components/network.hpp"

class ModelSerializer {
public:
  static void save(const Network& network,
                   const std::string& path);

  static Network load(const std::string& path);
};

#endif // MODEL_SERIALIZER_HPP

#include "helpers/ModelSerializer.hpp"
#include "helpers/ModelPersist.hpp"

void ModelSerializer::save(const Network& network,
                           const std::string& path) {
  ModelPersistStructure(network.getLayers(), 
                        network.getTensorArena().getBuffer(),
                        network.getHiddenActivation(),
                        network.getOutputActivation())
    .persist(path);
}

Network ModelSerializer::load(const std::string& path) {
  const ModelPersistStructure persist_structure(path);

  return Network(persist_structure.getLayers(),
                 persist_structure.getHiddenActivation(),
                 persist_structure.getOutputActivation(),
                 persist_structure.getTensors());
}

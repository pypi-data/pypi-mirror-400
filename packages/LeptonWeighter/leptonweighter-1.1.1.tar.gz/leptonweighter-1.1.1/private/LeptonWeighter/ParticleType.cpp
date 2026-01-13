#include "LeptonWeighter/ParticleType.h"

namespace LW {

std::ostream& operator<<(std::ostream& os, ParticleType& pt) {
  os << std::to_string((int)pt);
  return os;
}

} // close LW namespace

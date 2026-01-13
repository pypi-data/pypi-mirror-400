#ifndef LW_UTILS_H
#define LW_UTILS_H

#include <iostream>
#include <assert.h>
#include <exception>
#include <stdexcept>
#include "LeptonWeighter/ParticleType.h"

namespace LW {
  bool isNeutrino(ParticleType p);
  bool isAntineutrino(ParticleType p);
  bool isLepton(ParticleType p);
  bool isCharged(ParticleType p);
  ParticleType deduceInitialType(ParticleType pType1, ParticleType pType2);
} // namespace LW

#endif

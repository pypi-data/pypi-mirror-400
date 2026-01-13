#include "LeptonWeighter/Utils.h"

namespace LW {

bool isNeutrino(ParticleType p){
      return(p==ParticleType::NuE
             || p==ParticleType::NuMu
             || p==ParticleType::NuTau);
}

bool isAntineutrino(ParticleType p){
      return(p==ParticleType::NuEBar
             || p==ParticleType::NuMuBar
             || p==ParticleType::NuTauBar);
}

bool isLepton(ParticleType p){
        return(p==ParticleType::EMinus   || p==ParticleType::EPlus ||
               p==ParticleType::MuMinus  || p==ParticleType::MuPlus ||
               p==ParticleType::TauMinus || p==ParticleType::TauPlus ||
               p==ParticleType::NuE      || p==ParticleType::NuEBar ||
               p==ParticleType::NuMu     || p==ParticleType::NuMuBar ||
               p==ParticleType::NuTau    || p==ParticleType::NuTauBar);
}

bool isCharged(ParticleType p){
        assert(isLepton(p) || p==ParticleType::Hadrons);
        return(p==ParticleType::EMinus   || p==ParticleType::EPlus ||
               p==ParticleType::MuMinus  || p==ParticleType::MuPlus ||
               p==ParticleType::TauMinus || p==ParticleType::TauPlus ||
               p==ParticleType::Hadrons);
}

// This function was copied from CW LeptonInjector implementation.
ParticleType deduceInitialType(ParticleType pType1, ParticleType pType2){
        //only accept certain particle types in general
        if(!isLepton(pType1) && pType1!=ParticleType::Hadrons)
          throw std::runtime_error("Unexpected particle type: "
                                   + std::to_string((int)pType1)
                                   + ";\nonly leptons and 'Hadrons' are supported");
        if(!isLepton(pType2) && pType2!=ParticleType::Hadrons)
          throw std::runtime_error("Unexpected particle type: "
                                   + std::to_string((int)pType2)
                                   + ";\nonly leptons and 'Hadrons' are supported");

        bool c1=isCharged(pType1);
        bool c2=isCharged(pType2);
        bool l1=isLepton(pType1);
        bool l2=isLepton(pType2);

        //at least one particle should be charged
        if(!c1 && !c2)
          throw std::runtime_error("Final state must contain at least one charged particle.\n Specified particles were " + std::to_string((int)pType1)+ " and " + std::to_string((int)pType2));

        //first particle is charged, second is not
        if(c1 && !c2){
                //valid cases are charged lepton + matching antineutrino for GR
                if(l1){
                        //!c2 => pType2 is a neutrino
                        if(!((pType1==ParticleType::EMinus   && pType2==ParticleType::NuEBar) ||
                                 (pType1==ParticleType::EPlus    && pType2==ParticleType::NuE) ||
                                 (pType1==ParticleType::MuMinus  && pType2==ParticleType::NuMuBar) ||
                                 (pType1==ParticleType::MuPlus   && pType2==ParticleType::NuMu) ||
                                 (pType1==ParticleType::TauMinus && pType2==ParticleType::NuTauBar) ||
                                 (pType1==ParticleType::TauPlus  && pType2==ParticleType::NuTau)))
                                throw std::runtime_error("Final states with a charged lepton must have an anti-matching neutrino.\n Specified particles were " + std::to_string((int)pType1) + " and " + std::to_string((int)pType2));
                        return(ParticleType::NuEBar);
                }
                throw std::runtime_error("Unrecognized final state type: " + std::to_string((int)pType1) + " and " + std::to_string((int)pType2));
        }

        //first particle is neutral, second is charged
        if(!c1 && c2){
                if(l1 && pType2==ParticleType::Hadrons){
                        //particle 1 is a neutral lepton, so it must be a neutrino
                        return(pType1); //the incoming neutrino type is the same as the outgoing
                }
                throw std::runtime_error("Unrecognized final state type: " + std::to_string((int)pType1) + " and " + std::to_string((int)pType2));
        }

        //have two charged particles
        if(c1 && c2){
                //no two charged lepton states
                if(l1 && l2)
                        throw std::runtime_error("Two charged lepton final states are not allowed.\n Specified particles were " + std::to_string((int)pType1) + " and " + std::to_string((int)pType2));
                //lepton should be given first
                if(!l1 && l2)
                        throw std::runtime_error("Final states should specify charged leptons before 'Hadrons'.\n Specified particles were " + std::to_string((int)pType1) + " and " + std::to_string((int)pType2));

                if(l1 && !l2){ //valid: charged lepton + Hadrons for CC
                        //throw std::runtime_error(std::to_string((int)pType1) + ", " + std::to_string((int)pType2) + " identified as Charged Current");
                        switch(pType1){
                                case ParticleType::EMinus: return(ParticleType::NuE);
                                case ParticleType::EPlus: return(ParticleType::NuEBar);
                                case ParticleType::MuMinus: return(ParticleType::NuMu);
                                case ParticleType::MuPlus: return(ParticleType::NuMuBar);
                                case ParticleType::TauMinus: return(ParticleType::NuTau);
                                case ParticleType::TauPlus: return(ParticleType::NuTauBar);
                                default: assert(false && "This point should be unreachable");
                        }
                }
                if(!l1 && !l2){ //valid: two hadrons (for GR)
                  //std::cerr << (std::to_string((int)pType1) + ", " + std::to_string((int)pType2) + " identified as Glashow Resonance (hadronic)");
                        return(ParticleType::NuEBar);
                }
        }
        std::runtime_error("Logic error; this point should be unreachable");
        return ParticleType::Impossible;
}

}// namespace LW


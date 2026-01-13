#include "LeptonWeighter/nuSQFluxInterface.h"

namespace LW {

ParticleType Convert_nuSQuIDS_Id_To_PDG_Id(unsigned int flv, unsigned int neutype){
  if(flv == 0 and neutype == 0)
    return LW::ParticleType::NuE;
  else if(flv == 0 and neutype == 1)
    return LW::ParticleType::NuEBar;
  else if(flv == 1 and neutype == 0)
    return LW::ParticleType::NuMu;
  else if(flv == 1 and neutype == 1)
    return LW::ParticleType::NuMuBar;
  else if(flv == 2 and neutype == 0)
    return LW::ParticleType::NuTau;
  else if(flv == 2 and neutype == 1)
    return LW::ParticleType::NuTauBar;
  else
    throw std::runtime_error("LeptonWeighter::nuSQFluxInterface: Invalid nusquids identifier provided when trying to convert to LW::ParticleType.");
}

std::pair<unsigned int, unsigned int> Convert_PDG_Id_To_nuSQuIDS_Id(ParticleType pt){
  unsigned int neutype = (int)(pt) > 0 ? 0 : 1;
  unsigned int flavor;
  switch(pt){
    case LW::ParticleType::NuE     : flavor = 0;break;
    case LW::ParticleType::NuEBar  : flavor = 0;break;
    case LW::ParticleType::NuMu    : flavor = 1;break;
    case LW::ParticleType::NuMuBar : flavor = 1;break;
    case LW::ParticleType::NuTau   : flavor = 2;break;
    case LW::ParticleType::NuTauBar: flavor = 2;break;
    default: std::runtime_error("LeptonWeighter::nuSQFluxInterface: Particle type cannot be converted to a nusquids type.");
  }
  return std::make_pair(flavor,neutype);
}

} // close LW namespace

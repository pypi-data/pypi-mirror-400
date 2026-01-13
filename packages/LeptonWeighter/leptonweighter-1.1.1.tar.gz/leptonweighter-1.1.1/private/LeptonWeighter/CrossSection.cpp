#include <LeptonWeighter/CrossSection.h>
#include <math.h>
#include <iostream>
#include <cassert>

namespace LW {

bool CrossSectionFromSpline::is_charged_lepton(ParticleType p) const {
    using PT=ParticleType;
    if(p == PT::EPlus or p == PT::EMinus or p == PT::MuPlus or p == PT::MuMinus or p == PT::TauPlus or p == PT::TauMinus)
        return true;
    return false;
}

double CrossSectionFromSpline::DoubleDifferentialCrossSection(ParticleType particle, ParticleType f0, ParticleType f1, double nuEnergy,double x, double y) const {
    int centerbuffer[3];
    double xx[3];

    xx[0] = log10(nuEnergy);
    xx[1] = log10(x);
    xx[2] = log10(y);

    double diffxs=0;

    if (particle == ParticleType::NuE or particle == ParticleType::NuMu or particle == ParticleType::NuTau){
        if(is_charged_lepton(f0) or is_charged_lepton(f1)){
            // charged current interaction
            if(nu_CC_dsdxdy->searchcenters(xx,centerbuffer))
                diffxs += pow(10.0,nu_CC_dsdxdy->ndsplineeval(xx,centerbuffer,0));
        } else {
            // neutral current interaction
            if(nu_NC_dsdxdy->searchcenters(xx,centerbuffer))
                diffxs += pow(10.0,nu_NC_dsdxdy->ndsplineeval(xx,centerbuffer,0));
        }
    }
    else if (particle == ParticleType::NuEBar or particle == ParticleType::NuMuBar or particle == ParticleType::NuTauBar){
        if(is_charged_lepton(f0) or is_charged_lepton(f1)){
            // charged current interaction
            if(nubar_CC_dsdxdy->searchcenters(xx,centerbuffer))
                diffxs += pow(10.0,nubar_CC_dsdxdy->ndsplineeval(xx,centerbuffer,0));
        } else {
            // neutral current interaction
            if(nubar_NC_dsdxdy->searchcenters(xx,centerbuffer))
                diffxs += pow(10.0,nubar_NC_dsdxdy->ndsplineeval(xx,centerbuffer,0));
        }
    }
    else {
        throw std::runtime_error("CrossSection:CalDDXSPhotoSpline : Bad PDG type.");
    }

    return msq_tocmsq*diffxs;
}

CrossSectionFromSpline::CrossSectionFromSpline(
        std::string differential_neutrino_CC_xs_spline_path, std::string differential_antineutrino_CC_xs_spline_path,
        std::string differential_neutrino_NC_xs_spline_path, std::string differential_antineutrino_NC_xs_spline_path):
    nu_CC_dsdxdy(new photospline::splinetable<>),
    nubar_CC_dsdxdy(new photospline::splinetable<>),
    nu_NC_dsdxdy(new photospline::splinetable<>),
    nubar_NC_dsdxdy(new photospline::splinetable<>)
{
    if(not nu_CC_dsdxdy->read_fits(differential_neutrino_CC_xs_spline_path))
        throw std::runtime_error("Error loading differential CC neutrino the spline.");

    if(not nubar_CC_dsdxdy->read_fits(differential_antineutrino_CC_xs_spline_path))
        throw std::runtime_error("Error loading differential CC antineutrino spline.");

    if(not nu_NC_dsdxdy->read_fits(differential_neutrino_NC_xs_spline_path))
        throw std::runtime_error("Error loading differential NC neutrino the spline.");

    if(not nubar_NC_dsdxdy->read_fits(differential_antineutrino_NC_xs_spline_path))
        throw std::runtime_error("Error loading differential NC antineutrino spline.");
}


#ifdef NUS_FOUND
double GlashowResonanceCrossSection::DoubleDifferentialCrossSection(ParticleType pt, ParticleType finalstate_0, ParticleType finalstate_1, double energy, double x, double y) const {
  if(pt == ParticleType::NuEBar){
    // GR support comes from nusquids. CAD
    using namespace nusquids;
    double GeV = 1.e9;
    double e_out = (1-y)*energy;
    double cm2_to_m2 = 1.e-4; //convert from nuSQuIDs units to LW units!

    //K. Olive et al. (PDG), Chin. Phys. C38, 090001 (2014)
    double b_muon = 0.1063;
    double b_elec = 0.1071;
    double b_tau  = 0.1138;
    double b_hadr = 0.6741;
    double scale = 1.0/b_muon;

    if (finalstate_0 == ParticleType::EMinus || finalstate_0 == ParticleType::NuEBar){
        scale*=b_elec;
    }else if (finalstate_0 == ParticleType::MuMinus || finalstate_0 == ParticleType::NuMuBar){
        scale*=b_muon;
    }else if (finalstate_0 == ParticleType::TauMinus || finalstate_0 == ParticleType::NuTauBar){
        scale*=b_tau;
    }else if (finalstate_0 == ParticleType::Hadrons){
        scale*=b_hadr;
    }

    return scale*cm2_to_m2*grxs.SingleDifferentialCrossSection(energy*GeV,e_out*GeV,
            NeutrinoCrossSections::electron,NeutrinoCrossSections::antineutrino,NeutrinoCrossSections::GR);
  } else {
    return 0.;
  }
}
#endif

} // namespace LW


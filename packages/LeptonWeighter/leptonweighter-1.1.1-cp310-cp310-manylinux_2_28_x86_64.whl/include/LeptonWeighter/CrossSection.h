#ifndef LW_CROSSSECTION_H
#define LW_CROSSSECTION_H

#include <LeptonWeighter/ParticleType.h>
#include <LeptonWeighter/Event.h>
#include <LeptonWeighter/MetaWeighter.h>
#include <LeptonWeighter/Constants.h>
#include <photospline/splinetable.h>
#include <photospline/bspline.h>
#include <memory>

#ifdef NUS_FOUND
#include <nuSQuIDS/xsections.h>
#endif

namespace LW {

// Within the following classes:
// x refers to the Feynman scaling variable
// y refers to the inelasticity
// in the glashow resonance case x is ignored
// In either case the y definition follows
// the DIS converntion.

///\class
///\brief Abstract cross section class
class CrossSection: public MetaWeighter<CrossSection> {
    public:
        virtual double DoubleDifferentialCrossSection(ParticleType pt, ParticleType f0, ParticleType f1, double energy, double x, double y) const = 0;

        template<typename Event>
        double operator()(const Event& e) const {
            return DoubleDifferentialCrossSection(e.primary_type, e.final_state_particle_0, e.final_state_particle_1, e.energy, e.interaction_x, e.interaction_y);
        }
};

///\class
///\brief Cross section from spline class
class CrossSectionFromSpline: public CrossSection {
    private:
        bool is_charged_lepton(ParticleType pt) const;
        const double msq_tocmsq = 1.e4;
    private:
        // photospline objects
        using splinetable=photospline::splinetable<>;
        std::shared_ptr<splinetable> nu_CC_dsdxdy;
        std::shared_ptr<splinetable> nubar_CC_dsdxdy;
        std::shared_ptr<splinetable> nu_NC_dsdxdy;
        std::shared_ptr<splinetable> nubar_NC_dsdxdy;
    public:
        ///\brief Constructor
        CrossSectionFromSpline(std::string differential_neutrino_CC_xs_spline_path, std::string differential_antineutrino_CC_xs_spline_path,
                std::string differential_neutrino_NC_xs_spline_path, std::string differential_antineutrino_NC_xs_spline_path);
        ///\brief Returns double differential cross section in cm^2.
        double DoubleDifferentialCrossSection(ParticleType pt, ParticleType finalstate_0, ParticleType finalstate_1, double energy, double x, double y) const override;
};

#ifdef NUS_FOUND
///\class
///\brief Cross section from spline class
class GlashowResonanceCrossSection: public CrossSection {
    private:
        nusquids::GlashowResonanceCrossSection grxs;
    public:
        ///\brief Constructor
        GlashowResonanceCrossSection(){}
        ///\brief Returns single differential cross section in cm^2. The x-argument is ignored;
        double DoubleDifferentialCrossSection(ParticleType pt, ParticleType finalstate_0, ParticleType finalstate_1, double energy, double x, double y) const override;
};
#endif

} // namespace LW

#endif

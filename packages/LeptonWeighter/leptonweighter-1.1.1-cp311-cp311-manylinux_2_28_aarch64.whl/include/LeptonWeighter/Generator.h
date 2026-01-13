#ifndef LW_GENERATOR_H
#define LW_GENERATOR_H

/*
   “I don’t feel very much like Pooh today," said Pooh.
   "There there," said Piglet. "I’ll bring you tea and honey until you do.” ― A.A. Milne, Winnie-the-Pooh
 */

#include <iostream>
#include <memory>
#include <photospline/splinetable.h>
#include <LeptonWeighter/MetaWeighter.h>
#include <LeptonWeighter/Event.h>
#include <LeptonWeighter/Utils.h>
#include <LeptonWeighter/LeptonInjectorConfigReader.h>

#ifdef NUS_FOUND
#include <nuSQuIDS/xsections.h>
#endif

namespace LW {

///\class
///\brief SimulationDetail class
class SimulationDetails {
    protected:
        const unsigned long numberOfEvents;
        const unsigned int year;
        const ParticleType final_state_particle_0;
        const ParticleType final_state_particle_1;
        const double azimuthMin;
        const double azimuthMax;
        const double zenithMin;
        const double zenithMax;
        const double energyMin;
        const double energyMax;
        const double powerlawIndex;
        std::shared_ptr<photospline::splinetable<>> differential_cross_section_spline;
        std::shared_ptr<photospline::splinetable<>> total_cross_section_spline;
    protected:
        static bool CheckParticleEnumeration(EnumDefBlock) {return true;} // Let's believe. CAD
    public:
        ///\brief Constructor
        SimulationDetails(unsigned long numberOfEvents,
                ParticleType final_state_particle_0, ParticleType final_state_particle_1,
                std::shared_ptr<photospline::splinetable<>> differential_cross_section_spline, std::shared_ptr<photospline::splinetable<>> total_cross_section_spline,
                unsigned int year,
                double azimuthMin, double azimuthMax,
                double zenithMin, double zenithMax,
                double energyMin, double energyMax, double powerlawIndex):
            numberOfEvents(numberOfEvents),year(year),
            final_state_particle_0(final_state_particle_0),final_state_particle_1(final_state_particle_1),
            azimuthMin(azimuthMin),azimuthMax(azimuthMax),
            zenithMin(zenithMin),zenithMax(zenithMax),
            energyMin(energyMin),energyMax(energyMax),powerlawIndex(powerlawIndex),
            differential_cross_section_spline(differential_cross_section_spline),total_cross_section_spline(total_cross_section_spline)
    {}
    public:
        ///\brief Returns minimum generation energy in GeV.
        double Get_MinEnergy() const { return energyMin;}
        ///\brief Returns maximum generation energy in GeV.
        double Get_MaxEnergy() const { return energyMax;}
        ///\brief Returns minimum generation zenith angle in radians.
        double Get_MinZenith() const { return zenithMin;}
        ///\brief Returns maximum generation zenith angle in radians.
        double Get_MaxZenith() const { return zenithMax;}
        ///\brief Returns minimum generation azimuthal angle in radians.
        double Get_MinAzimuth() const { return azimuthMin;}
        ///\brief Returns maximum generation azimuthal angle in radians.
        double Get_MaxAzimuth() const { return azimuthMax;}
        ///\brief Returns total number of generated events.
        unsigned long Get_NumberOfEvents() const { return numberOfEvents;}
        ///\brief Returns year of validity for this simulation. LEGACY
        unsigned long Get_Year() const { return year;}
        ///\brief Returns final state particle 0 type
        ParticleType Get_ParticleType0() const { return final_state_particle_0;}
        ///\brief Returns final state particle 1 type
        ParticleType Get_ParticleType1() const { return final_state_particle_1;}
        ///\brief Return power law index
        double Get_PowerLawIndex() const { return powerlawIndex;}
        ///\brief Return double differential cross section spline
        std::shared_ptr<const photospline::splinetable<>> Get_DifferentialSpline() const { return differential_cross_section_spline;}
        ///\brief Return total cross section spline
        std::shared_ptr<const photospline::splinetable<>> Get_TotalSpline() const { return total_cross_section_spline;}
};

///\class
///\brief RangeSimulation class
class RangeSimulationDetails : public SimulationDetails{
    private:
        ///\brief Deserializer function from little endian binary file
        ///@param configuration_filename absolute path to .lic file
        static RangeSimulationDetails ReadFromFile(std::string configuration_filename);
    protected:
        const double injectionRadius;
        const double injectionCap;
    public:
        ///\brief Constructor
        template<typename... ArgTypes>
        RangeSimulationDetails(double injectionRadius, double injectionCap, ArgTypes&&... args):
            SimulationDetails(args...),
            injectionRadius(injectionRadius),injectionCap(injectionCap)
    {}
        ///\brief Constructor from file
        explicit RangeSimulationDetails(const std::string & configuration_filename): RangeSimulationDetails(ReadFromFile(configuration_filename)){}
        static RangeSimulationDetails MakeFromRangeInjectorConfiguration(const RangedInjectionConfiguration);
    public:
        ///\brief Return injection radius in meters
        double Get_InjectionRadius() const { return injectionRadius;}
        ///\brief Return injection cap in meters
        double Get_InjectionCap() const { return injectionCap;}
};

///\class
///\brief VolumeSimulation class
class VolumeSimulationDetails : public SimulationDetails{
    private:
        ///\brief Deserializer function from little endian binary file
        ///@param configuration_filename absolute path to .lic file
        static VolumeSimulationDetails ReadFromFile(std::string configuration_filename);
    protected:
        const double cylinderRadius;
        const double cylinderHeight;
    public:
        ///\brief Constructor
        template<typename... ArgTypes>
        VolumeSimulationDetails(double cylinderRadius, double cylinderHeight, ArgTypes&&... args):
            SimulationDetails(args...),
            cylinderRadius(cylinderRadius),cylinderHeight(cylinderHeight)
    {}
        ///\brief Constructor from file
        explicit VolumeSimulationDetails(const std::string & configuration_filename): VolumeSimulationDetails(ReadFromFile(configuration_filename)){}
        static VolumeSimulationDetails MakeFromVolumeInjectorConfiguration(const VolumeInjectionConfiguration);
    public:
        double Get_CylinderHeight() const { return cylinderHeight;}
        double Get_CylinderRadius() const { return cylinderRadius;}
};

///\class
///\brief Generator abstract class
class Generator: public MetaWeighter<Generator> {
    private:
#ifdef NUS_FOUND
        nusquids::GlashowResonanceCrossSection grxs;
#endif
    protected:
        const SimulationDetails sim_details;
    protected:
        virtual double probability_stat() const;
        virtual double probability_e(double e) const;
        virtual double probability_dir(double zenith, double azimuth) const;
        virtual double probability_final_state(ParticleType final_state_particle_0,ParticleType primary_state_particle_1) const;
        virtual double probability_area() const = 0;
        virtual double probability_pos(double x, double y, double z,double zenith, double azimuth) const = 0;
        virtual double probability_interaction(double e, double y, double number_of_targets) const;
        virtual double probability_interaction(double e, double x, double y, double number_of_targets) const;
        virtual double get_eff_height(double x, double y, double z, double zenith, double azimuth) const = 0;
        virtual double number_of_targets(Event& e) const = 0;
    public:
        ///\brief Constructor
        explicit Generator(SimulationDetails sim_details):sim_details(sim_details){}
        ///\brief Return the probability of generating the event
        double probability(Event & e) const;
        double operator()(Event & e) const { return probability(e);}
};

///\class
///\brief RangeGenerator class
class RangeGenerator: public Generator {
    const RangeSimulationDetails range_sim_details;
    protected:
    double probability_area() const override;
    double probability_pos(double x, double y, double z, double zenith, double azimuth) const override {return 1;}
    double get_eff_height(double x, double y, double z, double zenith, double azimuth) const override {return 1;}
    virtual double number_of_targets(Event& e) const override;
    public:
    ///\brief Constructor
    explicit RangeGenerator(RangeSimulationDetails sim_details):Generator(sim_details),range_sim_details(sim_details){};
    RangeSimulationDetails GetSimulationDetails() const {return range_sim_details;};
};

///\class
///\brief VolumeGenerator class
class VolumeGenerator: public Generator {
    const VolumeSimulationDetails vol_sim_details;
    protected:
    double probability_area() const override {return 1;}
    double probability_pos(double x, double y, double z, double zenith, double azimuth) const override;
    double get_eff_height(double x, double y, double z, double zenith, double azimuth) const override;
    virtual double number_of_targets(Event& e) const override;
    public:
    ///\brief Constructor
    explicit VolumeGenerator(VolumeSimulationDetails sim_details):Generator(sim_details),vol_sim_details(sim_details){};
    VolumeSimulationDetails GetVolumeSimulationDetails() {return vol_sim_details;}
};

std::vector<std::shared_ptr<Generator>> MakeGeneratorsFromLICFile(std::string filename);
std::vector<std::shared_ptr<Generator>> MakeGeneratorsFromH5File(std::string filename);

//std::ostream& operator<<(std::ostream& os, RangeSimulationDetails& e);
//std::ostream& operator<<(std::ostream& os, VolumeSimulationDetails& e);

} // namespace LW

#endif

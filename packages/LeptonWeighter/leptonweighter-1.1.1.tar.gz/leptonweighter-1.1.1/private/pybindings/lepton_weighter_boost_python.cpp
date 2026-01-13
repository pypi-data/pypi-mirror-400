#include <boost/python.hpp>
#include <boost/python/scope.hpp>
#include <boost/python/to_python_converter.hpp>
#include <boost/python/overloads.hpp>
#include <LeptonWeighter/Event.h>
#include <LeptonWeighter/ParticleType.h>
#define NUS_FOUND
#include <LeptonWeighter/Weighter.h>
#include <LeptonWeighter/nuSQFluxInterface.h>
#include "container_conversions.h"

using namespace boost::python;
using namespace LW;

template<class T>
struct VecToList
{
  static PyObject* convert(const std::vector<T>& vec){
    boost::python::list* l = new boost::python::list();
    for(size_t i =0; i < vec.size(); i++)
      (*l).append(vec[i]);

    return l->ptr();
  }
};

// LeptonWeighter Python Bindings module definitions

BOOST_PYTHON_MODULE(LeptonWeighter)
{

    //========================================================//
    // PARTICLE ENUM //
    //========================================================//

    enum_<ParticleType>("ParticleType")
        .value("NuE",ParticleType::NuE)
        .value("NuMu",ParticleType::NuMu)
        .value("NuTau",ParticleType::NuTau)
        .value("NuEBar",ParticleType::NuEBar)
        .value("NuMuBar",ParticleType::NuMuBar)
        .value("NuTauBar",ParticleType::NuTauBar)

        .value("EMinus",ParticleType::EMinus)
        .value("EPlus",ParticleType::EPlus)
        .value("MuMinus",ParticleType::MuMinus)
        .value("MuPlus",ParticleType::MuPlus)
        .value("TauMinus",ParticleType::TauMinus)
        .value("TauPlus",ParticleType::TauPlus)

        .value("unknown",ParticleType::unknown)
        .value("Hadrons",ParticleType::Hadrons)
        ;

    //========================================================//
    // GENERATORS //
    //========================================================//
    class_<SimulationDetails, boost::noncopyable, std::shared_ptr<SimulationDetails>>("SimulationDetails", no_init)
        .add_property("numberOfEvents",&SimulationDetails::Get_NumberOfEvents)
        .add_property("year",&SimulationDetails::Get_Year)
        .add_property("final_state_particle_0",&SimulationDetails::Get_ParticleType0)
        .add_property("final_state_particle_1",&SimulationDetails::Get_ParticleType1)
        .add_property("azimuthMin",&SimulationDetails::Get_MinAzimuth)
        .add_property("azimuthMax",&SimulationDetails::Get_MaxAzimuth)
        .add_property("zenithMin",&SimulationDetails::Get_MinZenith)
        .add_property("zenithMax",&SimulationDetails::Get_MaxZenith)
        .add_property("energyMin",&SimulationDetails::Get_MinEnergy)
        .add_property("energyMax",&SimulationDetails::Get_MaxEnergy)
        .add_property("powerlawIndex",&SimulationDetails::Get_PowerLawIndex)
        .add_property("differential_cross_section_spline",&SimulationDetails::Get_DifferentialSpline)
        .add_property("total_cross_section_spline",&SimulationDetails::Get_TotalSpline)
        ;

    // abstract generator
    class_<Generator, std::shared_ptr<Generator>, boost::noncopyable>("Generator",no_init)
        .def("probability",&Generator::probability)
        .def("__call__",pure_virtual(&Generator::operator()))
        ;

    // range generator
    class_<RangeSimulationDetails, bases<SimulationDetails>, boost::noncopyable, std::shared_ptr<RangeSimulationDetails>>("RangeSimulationDetails",init<std::string>(args("Path to configuration file (.lic)")))
        ;
    class_<RangeGenerator, boost::noncopyable, std::shared_ptr<RangeGenerator>>("RangeGenerator",init<RangeSimulationDetails>(args("Configuration structure")))
        .add_property("range_sim_details",&RangeGenerator::GetSimulationDetails)
        ;

    implicitly_convertible< std::shared_ptr<RangeGenerator>, std::shared_ptr<Generator> >();

    // volume generator
    class_<VolumeSimulationDetails, bases<SimulationDetails>, boost::noncopyable, std::shared_ptr<VolumeSimulationDetails>>("VolumeSimulationDetails",init<std::string>(args("Path to configuration file (.lic)")))
        ;
    class_<VolumeGenerator, boost::noncopyable, std::shared_ptr<VolumeGenerator>>("VolumeGenerator",init<VolumeSimulationDetails>(args("Configuration structure")))
        .add_property("volume_sim_details",&VolumeGenerator::GetVolumeSimulationDetails)
        ;

    implicitly_convertible< std::shared_ptr<VolumeGenerator>, std::shared_ptr<Generator> >();

    //========================================================//
    // EVENTS //
    //========================================================//

    class_<Event, std::shared_ptr<Event>>("Event")
        .def_readwrite("primary_type",&Event::primary_type)
        .def_readwrite("final_state_particle_0",&Event::final_state_particle_0)
        .def_readwrite("final_state_particle_1",&Event::final_state_particle_1)
        .def_readwrite("interaction_x",&Event::interaction_x)
        .def_readwrite("interaction_y",&Event::interaction_y)
        .def_readwrite("energy",&Event::energy)
        .def_readwrite("azimuth",&Event::azimuth)
        .def_readwrite("zenith",&Event::zenith)
        .def_readwrite("x",&Event::x)
        .def_readwrite("y",&Event::y)
        .def_readwrite("z",&Event::z)
        .def_readwrite("radius",&Event::radius)
        .def_readwrite("total_column_depth",&Event::total_column_depth)
        ;

    //========================================================//
    // FLUX //
    //========================================================//

    class_<Flux, std::shared_ptr<Flux>, boost::noncopyable>("Flux",no_init)
        .def("__call__",pure_virtual(&Flux::operator()))
        ;

    class_<ConstantFlux, std::shared_ptr<ConstantFlux>, boost::noncopyable>("ConstantFlux",init<double>(args("Constant flux value in units 1/(GeV cm s sr)")))
        ;
    implicitly_convertible< std::shared_ptr<ConstantFlux>, std::shared_ptr<Flux> >();

    class_<nuSQUIDSAtmFlux<>, std::shared_ptr<nuSQUIDSAtmFlux<>>, boost::noncopyable>("nuSQUIDSAtmFlux",init<std::string>(args("Path to nusquids atmospheric file")))
        ;
    implicitly_convertible< std::shared_ptr<nuSQUIDSAtmFlux<>>, std::shared_ptr<Flux> >();

    class_<nuSQUIDSFlux, std::shared_ptr<nuSQUIDSFlux>, boost::noncopyable>("nuSQUIDSFlux",init<std::string>(args("Path to nusquids file")))
        ;
    class_<PowerLawFlux, std::shared_ptr<PowerLawFlux>, boost::noncopyable>("PowerLawFlux",init<double, double, double>(args("normalization","spectral index","pivot point")))
        ;

    implicitly_convertible< std::shared_ptr<ConstantFlux>, std::shared_ptr<Flux> >();
    implicitly_convertible< std::shared_ptr<nuSQUIDSAtmFlux<>>, std::shared_ptr<Flux> >();
    implicitly_convertible< std::shared_ptr<nuSQUIDSFlux>, std::shared_ptr<Flux> >();
    implicitly_convertible< std::shared_ptr<PowerLawFlux>, std::shared_ptr<Flux> >();

    //========================================================//
    // Cross Section //
    //========================================================//

    class_<CrossSection, boost::noncopyable>("CrossSection",no_init)
        .def("DoubleDifferentialCrossSection",pure_virtual(&CrossSection::DoubleDifferentialCrossSection))
        ;
    class_<CrossSectionFromSpline, std::shared_ptr<CrossSectionFromSpline>, boost::noncopyable>("CrossSectionFromSpline", 
            init<std::string,std::string,std::string,std::string>(args("CC diff neutrino cross section path", "CC diff antineutrino cross section path","NC diff neutrino cross section path","NC diff antineutrino cross section path")))
        ;
    class_<GlashowResonanceCrossSection, std::shared_ptr<GlashowResonanceCrossSection>, boost::noncopyable>("GlashowResonanceCrossSection");
    
    implicitly_convertible< std::shared_ptr<GlashowResonanceCrossSection>, std::shared_ptr<CrossSection> >();
    implicitly_convertible< std::shared_ptr<CrossSectionFromSpline>, std::shared_ptr<CrossSection> >();

    //========================================================//
    // Weighter //
    //========================================================//

    class_<Weighter, std::shared_ptr<Weighter> >("Weighter",init<std::shared_ptr<Flux>,std::shared_ptr<CrossSection>,std::shared_ptr<Generator>>(args("Flux","Cross section","Generator")))
        .def(init<std::vector<std::shared_ptr<Flux>>,std::shared_ptr<CrossSection>,std::shared_ptr<Generator>>(args("Vector of fluxes","Cross section","Generator")))
        .def(init<std::vector<std::shared_ptr<Flux>>,std::shared_ptr<CrossSection>,std::vector<std::shared_ptr<Generator>>>(args("Vector of fluxes","Cross section","Vector of generator")))
        .def(init<std::shared_ptr<Flux>,std::shared_ptr<CrossSection>,std::vector<std::shared_ptr<Generator>>>(args("Flux","Cross section","Vector of generator")))
        .def(init<std::shared_ptr<CrossSection>,std::vector<std::shared_ptr<Generator>>>(args("Cross section","Vector of generator")))
        .def(init<std::shared_ptr<CrossSection>,std::shared_ptr<Generator>>(args("Cross section","Generator")))
        .def("__call__",&Weighter::operator())
        .def("weight",&Weighter::weight)
        .def("get_oneweight",&Weighter::get_oneweight)
        .def("add_generator",&Weighter::add_generator)
        .def("add_flux",&Weighter::add_flux)
        .def("get_total_flux",&Weighter::get_total_flux)
        .def("get_oneweight",&Weighter::get_oneweight)
        .def("get_effective_tau_weight",&Weighter::get_effective_tau_weight)
        .def("get_effective_tau_oneweight",&Weighter::get_effective_tau_oneweight)
        ;

    //========================================================//
    // LIC GENERATOR READER //
    //========================================================//

    def("MakeGeneratorsFromLICFile",LW::MakeGeneratorsFromLICFile);

    //========================================================//
    // VECTOR CONVERSIONS //
    //========================================================//

    using namespace scitbx::boost_python::container_conversions;
    from_python_sequence< std::vector<std::shared_ptr<LW::Generator>>, variable_capacity_policy >();
    to_python_converter< std::vector<std::shared_ptr<LW::Generator>, class std::allocator<std::shared_ptr<LW::Generator>>>, VecToList<std::shared_ptr<LW::Generator>> > ();

    from_python_sequence< std::vector<std::shared_ptr<LW::Flux>>, variable_capacity_policy >();
    to_python_converter< std::vector<std::shared_ptr<LW::Flux>, class std::allocator<std::shared_ptr<LW::Flux>>>, VecToList<std::shared_ptr<LW::Flux>> > ();

} // close boost_python module

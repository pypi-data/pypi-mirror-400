#include <LeptonWeighter/Event.h>
#include <LeptonWeighter/ParticleType.h>
#include <LeptonWeighter/Weighter.h>

#ifdef NUS_FOUND
#include <LeptonWeighter/nuSQFluxInterface.h>
#endif

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

namespace py = pybind11;
using namespace LW;

// LeptonWeighter Python Bindings module definitions

PYBIND11_MODULE(LeptonWeighter, m)
{
    m.doc() = "LeptonWeighter Python Bindings"; // module docstring

    //========================================================//
    // PARTICLE ENUM //
    //========================================================//

    py::enum_<ParticleType>(m,"ParticleType")
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
        .export_values()
        ;

    //========================================================//
    // GENERATORS //
    //========================================================//

    // Abstract base class - no constructor exposed
    py::class_<SimulationDetails, std::shared_ptr<SimulationDetails>>(m,"SimulationDetails")
        .def_property_readonly("numberOfEvents",&SimulationDetails::Get_NumberOfEvents)
        .def_property_readonly("year",&SimulationDetails::Get_Year)
        .def_property_readonly("final_state_particle_0",&SimulationDetails::Get_ParticleType0)
        .def_property_readonly("final_state_particle_1",&SimulationDetails::Get_ParticleType1)
        .def_property_readonly("azimuthMin",&SimulationDetails::Get_MinAzimuth)
        .def_property_readonly("azimuthMax",&SimulationDetails::Get_MaxAzimuth)
        .def_property_readonly("zenithMin",&SimulationDetails::Get_MinZenith)
        .def_property_readonly("zenithMax",&SimulationDetails::Get_MaxZenith)
        .def_property_readonly("energyMin",&SimulationDetails::Get_MinEnergy)
        .def_property_readonly("energyMax",&SimulationDetails::Get_MaxEnergy)
        .def_property_readonly("powerlawIndex",&SimulationDetails::Get_PowerLawIndex)
        .def_property_readonly("differential_cross_section_spline",&SimulationDetails::Get_DifferentialSpline)
        .def_property_readonly("total_cross_section_spline",&SimulationDetails::Get_TotalSpline)
        ;

    // Abstract generator base class
    py::class_<Generator, std::shared_ptr<Generator>>(m,"Generator")
        .def("probability",&Generator::probability)
        ;

    // Range generator
    py::class_<RangeSimulationDetails, SimulationDetails, std::shared_ptr<RangeSimulationDetails>>(m,"RangeSimulationDetails")
        .def(py::init<std::string>(), py::arg("lic_file_path"))
        ;

    py::class_<RangeGenerator, Generator, std::shared_ptr<RangeGenerator>>(m,"RangeGenerator")
        .def(py::init<RangeSimulationDetails>(), py::arg("simulation_details"))
        .def_property_readonly("range_sim_details", &RangeGenerator::GetSimulationDetails)
        ;

    // Volume generator
    py::class_<VolumeSimulationDetails, SimulationDetails, std::shared_ptr<VolumeSimulationDetails>>(m,"VolumeSimulationDetails")
        .def(py::init<std::string>(), py::arg("lic_file_path"))
        ;

    py::class_<VolumeGenerator, Generator, std::shared_ptr<VolumeGenerator>>(m,"VolumeGenerator")
        .def(py::init<VolumeSimulationDetails>(), py::arg("simulation_details"))
        .def_property_readonly("volume_sim_details", &VolumeGenerator::GetVolumeSimulationDetails)
        ;

    //========================================================//
    // EVENTS //
    //========================================================//

    py::class_<Event, std::shared_ptr<Event>>(m,"Event")
        .def(py::init<>())
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

    // Abstract base class
    py::class_<Flux, std::shared_ptr<Flux>>(m,"Flux")
        .def("__call__",&Flux::operator())
        ;

    py::class_<ConstantFlux, Flux, std::shared_ptr<ConstantFlux>>(m,"ConstantFlux")
        .def(py::init<double>(), py::arg("constant_flux"))
        ;

#ifdef NUS_FOUND
    py::class_<nuSQUIDSAtmFlux<>, Flux, std::shared_ptr<nuSQUIDSAtmFlux<>>>(m,"nuSQUIDSAtmFlux")
        .def(py::init<std::string>(), py::arg("nusquids_atm_file"))
        ;

    py::class_<nuSQUIDSFlux, Flux, std::shared_ptr<nuSQUIDSFlux>>(m,"nuSQUIDSFlux")
        .def(py::init<std::string>(), py::arg("nusquids_file"))
        ;
#endif

    py::class_<PowerLawFlux, Flux, std::shared_ptr<PowerLawFlux>>(m,"PowerLawFlux")
        .def(py::init<double, double, double>(), py::arg("normalization"), py::arg("spectral_index"), py::arg("pivot_point"))
        ;

    //========================================================//
    // Cross Section //
    //========================================================//

    // Abstract base class
    py::class_<CrossSection, std::shared_ptr<CrossSection>>(m,"CrossSection")
        .def("DoubleDifferentialCrossSection",&CrossSection::DoubleDifferentialCrossSection)
        ;

    py::class_<CrossSectionFromSpline, CrossSection, std::shared_ptr<CrossSectionFromSpline>>(m,"CrossSectionFromSpline")
        .def(py::init<std::string,std::string,std::string,std::string>(),
             py::arg("cc_nu_xs_path"), py::arg("cc_nubar_xs_path"),
             py::arg("nc_nu_xs_path"), py::arg("nc_nubar_xs_path"))
        ;

#ifdef NUS_FOUND
    py::class_<GlashowResonanceCrossSection, CrossSection, std::shared_ptr<GlashowResonanceCrossSection>>(m,"GlashowResonanceCrossSection")
        .def(py::init<>())
        ;
#endif

    //========================================================//
    // Weighter //
    //========================================================//

    auto weighter_class = py::class_<Weighter, std::shared_ptr<Weighter>>(m,"Weighter")
        .def(py::init<std::shared_ptr<Flux>,std::shared_ptr<CrossSection>,std::shared_ptr<Generator>>(),
             py::arg("flux"), py::arg("cross_section"), py::arg("generator"))
        .def(py::init<std::vector<std::shared_ptr<Flux>>,std::shared_ptr<CrossSection>,std::shared_ptr<Generator>>(),
             py::arg("fluxes"), py::arg("cross_section"), py::arg("generator"))
        .def(py::init<std::vector<std::shared_ptr<Flux>>,std::shared_ptr<CrossSection>,std::vector<std::shared_ptr<Generator>>>(),
             py::arg("fluxes"), py::arg("cross_section"), py::arg("generators"))
        .def(py::init<std::shared_ptr<Flux>,std::shared_ptr<CrossSection>,std::vector<std::shared_ptr<Generator>>>(),
             py::arg("flux"), py::arg("cross_section"), py::arg("generators"))
        .def(py::init<std::shared_ptr<CrossSection>,std::vector<std::shared_ptr<Generator>>>(),
             py::arg("cross_section"), py::arg("generators"))
        .def(py::init<std::shared_ptr<CrossSection>,std::shared_ptr<Generator>>(),
             py::arg("cross_section"), py::arg("generator"))
        .def("__call__",&Weighter::operator())
        .def("weight",&Weighter::weight)
        .def("get_oneweight",&Weighter::get_oneweight)
        .def("add_generator",&Weighter::add_generator)
        .def("add_flux",&Weighter::add_flux)
        .def("get_total_flux",&Weighter::get_total_flux)
        ;

#ifdef NUS_FOUND
    weighter_class
        .def("get_effective_tau_weight",&Weighter::get_effective_tau_weight)
        .def("get_effective_tau_oneweight",&Weighter::get_effective_tau_oneweight)
        ;
#endif

    //========================================================//
    // LIC GENERATOR READER //
    //========================================================//

    m.def("MakeGeneratorsFromLICFile", &LW::MakeGeneratorsFromLICFile, py::arg("lic_file_path"));

} // close pybind11 module

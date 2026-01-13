#include <iostream>
#include <fstream>
#include <boost/version.hpp>
#if BOOST_VERSION < 107200
	#include <boost/detail/endian.hpp>
#else
	#include <boost/predef/other/endian.h>
#endif
#include <boost/lexical_cast.hpp>
#include <boost/format.hpp>
#include <boost/math/constants/constants.hpp>
#include <memory>
#include <vector>
#include <map>
#include <deque>
#include <iterator>
#include <set>
#include "LeptonWeighter/Weighter.h"

//==============================================================================================
//==============================================================================================

int main(int argc, char ** argv) {
    if(argc!=2)
        throw std::runtime_error("usage: configure.lic");

    std::string configuration_filename(argv[1]);
    std::vector<std::shared_ptr<LW::Generator>> generators = LW::MakeGeneratorsFromLICFile(configuration_filename);
    std::cout << "Number of generators in LIC file: " << generators.size() << std::endl;
    std::cout << std::endl;

    unsigned int i = 1;
    for (auto g : generators){
      std::cout << "Simulation details of generator " << i << std::endl;
      auto x = std::dynamic_pointer_cast<LW::RangeGenerator>(g)->GetSimulationDetails();

      std::cout << "Number of events per file:" << x.Get_NumberOfEvents() << std::endl;
      std::cout << "Final State Particle 0:" << (int)x.Get_ParticleType0() << std::endl;
      std::cout << "Final State Particle 1:" << (int)x.Get_ParticleType1() << std::endl;
      std::cout << "Minimum injected energy:" << x.Get_MinEnergy() << std::endl;
      std::cout << "Maximum injected energy:" << x.Get_MaxEnergy() << std::endl;
      std::cout << "Minimum zenith angle (rad):" << x.Get_MinZenith() << std::endl;
      std::cout << "Maximum zenith angle (rad):" << x.Get_MaxZenith() << std::endl;
      std::cout << "Minimum azimith angle (rad):" << x.Get_MinAzimuth() << std::endl;
      std::cout << "Maximum azimuth angle (rad):" << x.Get_MaxAzimuth() << std::endl;
      std::cout << "Injection power-law spectral index:" << x.Get_PowerLawIndex() << std::endl;
      std::cout << std::endl;

      i++;
    }

    return 0;
}


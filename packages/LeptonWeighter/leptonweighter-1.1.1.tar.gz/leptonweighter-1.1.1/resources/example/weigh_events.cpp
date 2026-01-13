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
#include <LeptonWeighter/Weighter.h>

//==============================================================================================
//==============================================================================================

#include "tableio.h"

herr_t collectTableNames(hid_t group_id, const char * member_name, void* operator_data){
    std::set<std::string>* items=static_cast<std::set<std::string>*>(operator_data);
    items->insert(member_name);
    return(0);
}

using Event=LW::Event;

template<typename CallbackType>
void readFile(const std::string& filePath, CallbackType action){
    H5File h5file(filePath);
    if(!h5file)
        throw std::runtime_error("Unable to open "+filePath);
    std::set<std::string> tables;
    H5Giterate(h5file,"/",NULL,&collectTableNames,&tables);
    if(tables.empty())
        throw std::runtime_error(filePath+" contains no tables");
#ifndef NO_STD_OUTPUT
    std::cout << "Reading " << filePath << std::endl;
#endif
    std::map<RecordID,Event> intermediateData;

    using particle = TableRow<field<double,CTS("totalEnergy")>,
          field<double,CTS("zenith")>,
          field<double,CTS("azimuth")>,
          field<double,CTS("finalStateX")>,
          field<double,CTS("finalStateY")>,
          field<int,CTS("finalType1")>,
          field<int,CTS("finalType2")>,
          field<int,CTS("initialType")>,
          field<double,CTS("totalColumnDepth")>,
          field<double,CTS("radius")>,
          field<double,CTS("z")>>;

    if(tables.count("EventProperties")){
        readTable<particle>(h5file, "EventProperties", intermediateData,
                [](const particle& p, Event& e){
                e.energy=p.get<CTS("totalEnergy")>();
                e.zenith=p.get<CTS("zenith")>();
                e.azimuth=p.get<CTS("azimuth")>();
                e.interaction_x=p.get<CTS("finalStateX")>();
                e.interaction_y=p.get<CTS("finalStateY")>();
                e.final_state_particle_0=static_cast<LW::ParticleType>(p.get<CTS("finalType1")>());
                e.final_state_particle_1=static_cast<LW::ParticleType>(p.get<CTS("finalType2")>());
                e.primary_type=static_cast<LW::ParticleType>(p.get<CTS("initialType")>());
                e.total_column_depth=p.get<CTS("totalColumnDepth")>();
                e.radius=p.get<CTS("radius")>();
                e.z=p.get<CTS("z")>();
                });
    }

    for(std::map<RecordID,Event>::value_type& item : intermediateData)
        action(item.first,item.second);
}

int main(int argc, char ** argv) {
    if(argc!=9)
        throw std::runtime_error("usage: main configure.lic diff_nu_xs_CC diff_nu_xs_NC diff_antinu_xs_CC diff_antinu_xs_NC nusquids_flux events_input_file.hdf5 output");

    std::string configuration_filename(argv[1]);
    std::string diff_nu_CC_xs(argv[2]);
    std::string diff_nu_NC_xs(argv[3]);
    std::string diff_antinu_CC_xs(argv[4]);
    std::string diff_antinu_NC_xs(argv[5]);
    std::string flux_filename(argv[6]);
    std::string input_filename(argv[7]);
    std::string output_filename(argv[8]);

    std::vector<std::shared_ptr<LW::Generator>> generators = LW::MakeGeneratorsFromLICFile(configuration_filename);
    std::shared_ptr<LW::CrossSectionFromSpline> xs = std::make_shared<LW::CrossSectionFromSpline>(diff_nu_CC_xs,diff_antinu_CC_xs,diff_nu_NC_xs,diff_antinu_NC_xs);
    LW::Weighter w(xs,generators);

    // read events from file
    std::deque<Event> events;
    try {
        readFile(input_filename,
                [&](RecordID id, Event& e){
                events.push_back(e);
                }
                );
    } catch ( std::exception & ex){
        std::cerr << ex.what() << std::endl;
    }

    std::cout << "FinalState0 \t FinalState1 \t InitialState \t Energy/GeV \t cos(th) \t azimuth/rad \t weight/Hz" << std::endl;

    for(auto& e: events){
        std::cout << (int)e.final_state_particle_0 << "\t" << (int)e.final_state_particle_1 << "\t" << (int)e.primary_type << "\t";
        std::cout << e.energy << "\t" << cos(e.zenith) << "\t" << e.azimuth << "\t";
        std::cout << w(e) << std::endl;
    }

    return 0;
}


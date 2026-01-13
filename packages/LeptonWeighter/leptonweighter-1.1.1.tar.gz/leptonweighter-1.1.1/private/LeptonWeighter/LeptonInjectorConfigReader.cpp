#include <LeptonWeighter/LeptonInjectorConfigReader.h>
#include <algorithm>

namespace{
bool isBigEndian(){
	static_assert(2*sizeof(char)==sizeof(uint16_t),
	"Endianness detection works only when sizeof(char) if half of sizeof(uint16_t)");
	const static uint16_t testValue=0x0001;
	const static char* readPtr=(const char*)&testValue;
	const static bool isBig=(readPtr==0);
	return isBig;
}
}

namespace LW {

std::istream& endianRead(std::istream& is, char* data, size_t dataSize){
    is.read(data,dataSize);
    //assume that input data is little endian. Reverse it if we are big endian
    if(isBigEndian())
        std::reverse(data,data+dataSize);
    if(!is.good())
        throw std::runtime_error("LWError: LeptonInjector little endian parsing failed.");
    return is;
}

std::istream& operator>>(std::istream& is, endianness_adapter<std::vector<char>>&& e){
    size_t size;
    is >> little_endian(size);
    e.t.resize(size);
    return(endianRead(is,&e.t[0],e.t.size()));
}

std::istream& operator>>(std::istream& is, endianness_adapter<std::string>&& e){
    size_t size;
    is >> little_endian(size);
    e.t.resize(size);
    return(endianRead(is,(char*)&e.t[0],e.t.size()));
}

std::istream& operator>>(std::istream& is, endianness_adapter<BlockHeader>&& e){
    is >> little_endian(e.t.block_length);
    is >> little_endian(e.t.block_name);
    is >> little_endian(e.t.block_version);
    return is;
}

std::ostream& operator<<(std::ostream& os, const BlockHeader& e){
    os << e.block_length << " " << e.block_name << " " << (int)e.block_version;
    return os;
}

std::istream& operator>>(std::istream& is, endianness_adapter<EnumDefBlock>&& e){
    is >> little_endian(e.t.enum_name);
    uint32_t size;
    is >> little_endian(size);
    e.t.enum_map.clear();
    for(unsigned int guy=0; guy < size; guy++){
        int64_t ii; std::string ss;
        is >> little_endian(ii);
        is >> little_endian(ss);
        e.t.enum_map.emplace(std::make_pair(ss,ii));
    }
    return is;
}

std::ostream& operator<<(std::ostream& os, const EnumDefBlock& e){
    os << e.enum_name << std::endl;
    for(auto guy : e.enum_map){
        os << guy.first << " " << guy.second << std::endl;
    }
    return os;
}

std::istream& operator>>(std::istream& is, endianness_adapter<RangedInjectionConfiguration>&& e){
    is >> little_endian(e.t.number_of_events);
    is >> little_endian(e.t.energyMin);
    is >> little_endian(e.t.energyMax);
    is >> little_endian(e.t.powerlawIndex);
    is >> little_endian(e.t.azimuthMin);
    is >> little_endian(e.t.azimuthMax);
    is >> little_endian(e.t.zenithMin);
    is >> little_endian(e.t.zenithMax);
    is >> little_endian(e.t.final_state_particle_0);
    is >> little_endian(e.t.final_state_particle_1);
    is >> little_endian(e.t.differentialCrossSectionData);
    is >> little_endian(e.t.totalCrossSectionData);
    is >> little_endian(e.t.injectionRadius);
    is >> little_endian(e.t.injectionCap);
    return is;
}

std::ostream& operator<<(std::ostream& os, RangedInjectionConfiguration& e){
    os << e.number_of_events << " ";
    os << e.energyMin << " ";
    os << e.energyMax << " ";
    os << e.powerlawIndex << " ";
    os << e.azimuthMax<< " ";
    os << e.azimuthMin << " ";
    os << e.zenithMin<< " ";
    os << e.zenithMax<< " ";
    os << (int)e.final_state_particle_0 << " ";
    os << (int)e.final_state_particle_1 << " ";
    os << sizeof(e.differentialCrossSectionData)<< " ";
    os << sizeof(e.totalCrossSectionData)<< " ";
    os << e.injectionRadius << " ";
    os << e.injectionCap;

    return os;
}

std::istream& operator>>(std::istream& is, endianness_adapter<VolumeInjectionConfiguration>&& e){
    is >> little_endian(e.t.number_of_events);
    is >> little_endian(e.t.energyMin);
    is >> little_endian(e.t.energyMax);
    is >> little_endian(e.t.powerlawIndex);
    is >> little_endian(e.t.azimuthMin);
    is >> little_endian(e.t.azimuthMax);
    is >> little_endian(e.t.zenithMin);
    is >> little_endian(e.t.zenithMax);
    is >> little_endian(e.t.final_state_particle_0);
    is >> little_endian(e.t.final_state_particle_1);
    is >> little_endian(e.t.differentialCrossSectionData);
    is >> little_endian(e.t.totalCrossSectionData);
    is >> little_endian(e.t.cylinderRadius);
    is >> little_endian(e.t.cylinderHeight);
    return is;
}

std::ostream& operator<<(std::ostream& os, VolumeInjectionConfiguration& e){
    os << e.number_of_events << " ";
    os << e.energyMin << " ";
    os << e.energyMax << " ";
    os << e.powerlawIndex << " ";
    os << e.azimuthMax<< " ";
    os << e.azimuthMin << " ";
    os << e.zenithMin<< " ";
    os << e.zenithMax<< " ";
    os << (int)e.final_state_particle_0 << " ";
    os << (int)e.final_state_particle_1 << " ";
    os << sizeof(e.differentialCrossSectionData)<< " ";
    os << sizeof(e.totalCrossSectionData)<< " ";
    os << e.cylinderRadius<< " ";
    os << e.cylinderHeight;

    return os;
}

} // namespace LW


#ifndef LW_LICONFREADER_H
#define LW_LICONFREADER_H

#include <map>
#include <iostream>
#include <memory>
#include <vector>
#include <LeptonWeighter/ParticleType.h>

namespace LW {

///A wrapper type which ensures that data read through it will be converted from
///little endian to the native endianness
template<typename T>
struct endianness_adapter{
    T& t;
    endianness_adapter(T& t):t(t){}
};

template<typename T>
endianness_adapter<T> little_endian(T& t){ return endianness_adapter<T>(t);}

// This function reads input data, assumed to be little endian, and performs
// byte swapping if necessary.
// This function must not be used directly on structures containing several
// fields which must be swapped individually, as it does not know how to do that.
std::istream& endianRead(std::istream& is, char* data, size_t dataSize);

template<typename T>
std::istream& operator>>(std::istream& is, endianness_adapter<T>&& e){
    return(endianRead(is,(char*)&e.t,sizeof(T)));
}

std::istream& operator>>(std::istream& is, endianness_adapter<std::vector<char>>&& e);
std::istream& operator>>(std::istream& is, endianness_adapter<std::string>&& e);

struct BlockHeader{
    uint64_t block_length;
    std::string block_name;
    uint8_t block_version;
};

std::istream& operator>>(std::istream& is, endianness_adapter<BlockHeader>&& e);
std::ostream& operator<<(std::ostream& os, const BlockHeader& e);

struct EnumDefBlock{
    std::string enum_name;
    std::map<std::string,int64_t> enum_map;
};

std::istream& operator>>(std::istream& is, endianness_adapter<EnumDefBlock>&& e);
std::ostream& operator<<(std::ostream& os, const EnumDefBlock& e);

struct RangedInjectionConfiguration {
    uint32_t number_of_events;
    double energyMin;
    double energyMax;
    double powerlawIndex;
    double azimuthMin;
    double azimuthMax;
    double zenithMin;
    double zenithMax;
    LW::ParticleType final_state_particle_0;
    LW::ParticleType final_state_particle_1;
    std::vector<char> differentialCrossSectionData;
    std::vector<char> totalCrossSectionData;
    double injectionRadius;
    double injectionCap;
};

std::istream& operator>>(std::istream& is, endianness_adapter<RangedInjectionConfiguration>&& e);
std::ostream& operator<<(std::ostream& os, RangedInjectionConfiguration& e);

struct VolumeInjectionConfiguration{
    uint32_t number_of_events;
    double energyMin;
    double energyMax;
    double powerlawIndex;
    double azimuthMin;
    double azimuthMax;
    double zenithMin;
    double zenithMax;
    LW::ParticleType final_state_particle_0;
    LW::ParticleType final_state_particle_1;
    std::vector<char> differentialCrossSectionData;
    std::vector<char> totalCrossSectionData;
    double cylinderRadius;
    double cylinderHeight;
};

std::istream& operator>>(std::istream& is, endianness_adapter<VolumeInjectionConfiguration>&& e);
std::ostream& operator<<(std::ostream& os, VolumeInjectionConfiguration& e);

} // namespace LW

#endif

#ifndef LW_EVENT_H
#define LW_EVENT_H

#include <LeptonWeighter/ParticleType.h>

namespace LW {

///\class
///\brief Event class
class Event {
    public:
        /// interaction primary
        ParticleType primary_type;

        /// interaction products
        ParticleType final_state_particle_0;
        ParticleType final_state_particle_1;

        /// interaction cross section kinematic variables
        double interaction_x;
        double interaction_y;

        /// primarty properties
        double energy;
        double azimuth;
        double zenith;

        /// interaction vertex position
        double x;
        double y;
        double z;

        // cylinder position
        double radius;

        // column density
        double total_column_depth;
};

} // namespace LW

#endif

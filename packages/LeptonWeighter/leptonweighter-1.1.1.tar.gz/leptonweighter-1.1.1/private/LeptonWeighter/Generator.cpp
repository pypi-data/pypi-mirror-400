#include <LeptonWeighter/Generator.h>
#include <LeptonWeighter/Constants.h>
#include <stdexcept>
#include <memory>
#include <fstream>
#include <cmath>
#include <hdf5.h>

//#define DEBUGPROBABILITY

namespace LW {

double Generator::probability(Event& e) const {
    double p;
    p = probability_e(e.energy);
#ifdef DEBUGPROBABILITY
    std::cout << std::endl << "Probability components" << std::endl;
    std::cout << "pe " << probability_e(e.energy) << std::endl;
#endif
    if(p==0)
        return 0;
    p *= probability_dir(e.zenith,e.azimuth);
#ifdef DEBUGPROBABILITY
    std::cout << "pdir " << probability_dir(e.zenith,e.azimuth) << " " << e.zenith << " " << std::endl;
#endif
    if(p==0)
        return 0;
    p *= probability_area();
#ifdef DEBUGPROBABILITY
    std::cout << "parea " << probability_area() << std::endl;
#endif
    if(p==0)
        return 0;
    p *= probability_pos(e.x,e.y,e.z, e.zenith, e.azimuth);
#ifdef DEBUGPROBABILITY
    std::cout << "ppos " << probability_pos(e.x,e.y,e.z, e.zenith, e.azimuth) << std::endl;
#endif
    if(p==0)
        return 0;
#ifdef DEBUGPROBABILITY
    std::cout << "pfs " << probability_final_state(e.final_state_particle_0,e.final_state_particle_1) << std::endl;
    std::cout << "pint " << probability_interaction(e.energy,e.interaction_x,e.interaction_y) << std::endl;
#endif
    return p*probability_stat()*probability_final_state(e.final_state_particle_0,e.final_state_particle_1)*
        probability_interaction(e.energy,e.interaction_y,number_of_targets(e))*probability_interaction(e.energy,e.interaction_x,e.interaction_y,number_of_targets(e));
}

double Generator::probability_final_state(ParticleType final_state_particle_0_,ParticleType final_state_particle_1_) const{
    if(sim_details.Get_ParticleType1() == final_state_particle_1_ and sim_details.Get_ParticleType0() == final_state_particle_0_)
        return 1.;
    else if (sim_details.Get_ParticleType0() == final_state_particle_1_ and sim_details.Get_ParticleType1() == final_state_particle_0_)
        return 1.;
    else
        return 0.;
}

double Generator::probability_e(double energy) const {
    double norm=0;
    double powerlawIndex=sim_details.Get_PowerLawIndex();
    double energyMin=sim_details.Get_MinEnergy();
    double energyMax=sim_details.Get_MaxEnergy();

    if(energy>energyMax or energy<energyMin)
        return 0;

    if(powerlawIndex!=1)
        norm=(1-powerlawIndex)/(pow(energyMax,1-powerlawIndex)-pow(energyMin,1-powerlawIndex));
    else if(powerlawIndex==1)
        norm=1./log(energyMax/energyMin);
    return (norm*pow(energy,-powerlawIndex));
}

double Generator::probability_dir(double zenith, double azimuth) const {
    if(zenith>sim_details.Get_MaxZenith() or zenith<sim_details.Get_MinZenith())
        return 0;
    if(azimuth>sim_details.Get_MaxAzimuth() or azimuth<sim_details.Get_MinAzimuth())
        return 0;
    return 1./((sim_details.Get_MaxAzimuth()-sim_details.Get_MinAzimuth())*(cos(sim_details.Get_MinZenith())-cos(sim_details.Get_MaxZenith())));
}

double Generator::probability_stat() const {
    return (sim_details.Get_NumberOfEvents());
}

double Generator::probability_interaction(double enu, double y,double number_of_events) const {
  return 1.;
  /*
   *  EXPERIMENTAL GLASHOW SAMPLER -- NOT USED
    if(deduceInitialType(sim_details.Get_ParticleType0(),sim_details.Get_ParticleType1()) == ParticleType::NuEBar){
      using namespace nusquids;
      // GR support comes from nusquids. CAD
      double GeV = 1.e9;
      double e_out = (1-y)*enu;
      double total_xs = grxs.TotalCrossSection(e_out*GeV,
              NeutrinoCrossSections::electron,NeutrinoCrossSections::antineutrino,NeutrinoCrossSections::GR);
      double diff_xs = grxs.SingleDifferentialCrossSection(enu*GeV,e_out*GeV,
              NeutrinoCrossSections::electron,NeutrinoCrossSections::antineutrino,NeutrinoCrossSections::GR);
      std::cout << "xsr" << diff_xs/total_xs << std::endl;
      return diff_xs/total_xs;
    } else {
      return 1.;
    }
  */
}

double Generator::probability_interaction(double enu, double x,double y,double number_of_targets) const {
    // DIS cross sections assumes all flavors to be equal in cross sections
    int centerbuffer[3];
    double xx[3];

    xx[0] = log10(enu);
    xx[1] = log10(x);
    xx[2] = log10(y);

    double differential_xs, total_xs;
    if(sim_details.Get_DifferentialSpline()->searchcenters(xx,centerbuffer))
        differential_xs = pow(10.0,sim_details.Get_DifferentialSpline()->ndsplineeval(xx,centerbuffer,0));
    else
        throw std::runtime_error("Could not evaluate total neutrino cross section spline.");
    if(sim_details.Get_TotalSpline()->searchcenters(xx,centerbuffer))
        total_xs = pow(10.0,sim_details.Get_TotalSpline()->ndsplineeval(xx,centerbuffer,0));
    else
        throw std::runtime_error("Could not evaluate total neutrino cross section spline.");

    return differential_xs/(1. - exp(-total_xs*number_of_targets));
}

double RangeGenerator::probability_area() const {
    return 1./(1e4*M_PI*range_sim_details.Get_InjectionRadius()*range_sim_details.Get_InjectionRadius());
}

RangeSimulationDetails RangeSimulationDetails::ReadFromFile(std::string configuration_filename){
    std::ifstream is(configuration_filename,std::ios::binary);
    BlockHeader h;
    // read first header
    is >> h;
    if(h.block_name != "EnumDef")
        throw std::runtime_error("LW::RangeSimulationDetails: Configuration file does not have a particle enumerator definitions.");
    if(not is.good() or is.eof())
        throw std::runtime_error("LW::RangeSimulationDetails: Configuration file error while reading.");
    EnumDefBlock edb;
    is >> edb;
    if(not CheckParticleEnumeration(edb))
        throw std::runtime_error("LW::RangeSimulationDetails: Configuration file particle enumeration are not compatible with current definitions. Alarm.");
    if(not is.good() or is.eof())
        throw std::runtime_error("LW::RangeSimulationDetails: Configuration file error while reading.");
    is >> h;
    if(h.block_name != "RangedInjectionConfiguration")
        throw std::runtime_error("LW::RangeSimulationDetails: Expected RangedInjectionConfiguration configuration block after enum definitions, but got " + h.block_name);
    RangedInjectionConfiguration ric;
    is >> ric;
    is.close();

    return MakeFromRangeInjectorConfiguration(ric);
}

RangeSimulationDetails RangeSimulationDetails::MakeFromRangeInjectorConfiguration(RangedInjectionConfiguration ric) {
    using splinetable_=photospline::splinetable<>;
    std::shared_ptr<splinetable_> differentialCrossSectionData = std::make_shared<splinetable_>();
    differentialCrossSectionData->read_fits_mem(ric.differentialCrossSectionData.data(),ric.differentialCrossSectionData.size());
    std::shared_ptr<splinetable_> totalCrossSectionData = std::make_shared<splinetable_>();
    totalCrossSectionData->read_fits_mem(ric.totalCrossSectionData.data(),ric.totalCrossSectionData.size());

    return RangeSimulationDetails(ric.injectionRadius,ric.injectionCap,
            ric.number_of_events,
            ric.final_state_particle_0,ric.final_state_particle_1,
            differentialCrossSectionData,totalCrossSectionData,
            0,// legacy. CAD
            ric.azimuthMin,ric.azimuthMax,ric.zenithMin,ric.zenithMax,ric.energyMin,ric.energyMax,ric.powerlawIndex);
}

VolumeSimulationDetails VolumeSimulationDetails::ReadFromFile(std::string configuration_filename){
    std::ifstream is(configuration_filename,std::ios::binary);
    BlockHeader h;
    // read first header
    is >> h;
    if(h.block_name != "EnumDef")
        throw std::runtime_error("LW::VolumeSimulationDetails: Configuration file does not have a particle enumerator definitions.");
    if(not is.good() or is.eof())
        throw std::runtime_error("LW::VolumeSimulationDetails: Configuration file error while reading.");
    EnumDefBlock edb;
    is >> edb;
    if(not CheckParticleEnumeration(edb))
        throw std::runtime_error("LW::VolumeSimulationDetails: Configuration file particle enumeration are not compatible with current definitions. Alarm.");
    if(not is.good() or is.eof())
        throw std::runtime_error("LW::VolumeSimulationDetails: Configuration file error while reading.");
    is >> h;
    if(h.block_name != "VolumeSimulationDetails")
        throw std::runtime_error("LW::VolumeSimulationDetails: Expected VolumeSimulationDetails configuration block after enum definitions, but got " + h.block_name);
    VolumeInjectionConfiguration vic;
    is >> vic;
    is.close();

    return MakeFromVolumeInjectorConfiguration(vic);
}

VolumeSimulationDetails VolumeSimulationDetails::MakeFromVolumeInjectorConfiguration(VolumeInjectionConfiguration vic){
    using splinetable_=photospline::splinetable<>;
    std::shared_ptr<splinetable_> differentialCrossSectionData = std::make_shared<splinetable_>();
    differentialCrossSectionData->read_fits_mem(vic.differentialCrossSectionData.data(),vic.differentialCrossSectionData.size());
    std::shared_ptr<splinetable_> totalCrossSectionData = std::make_shared<splinetable_>();
    totalCrossSectionData->read_fits_mem(vic.totalCrossSectionData.data(),vic.totalCrossSectionData.size());

    return VolumeSimulationDetails(vic.cylinderRadius,vic.cylinderHeight,
            vic.number_of_events,
            vic.final_state_particle_0,vic.final_state_particle_1,
            differentialCrossSectionData,totalCrossSectionData,
            0,// legacy. CAD
            vic.azimuthMin,vic.azimuthMax,vic.zenithMin,vic.zenithMax,vic.energyMin,vic.energyMax,vic.powerlawIndex);
}

double VolumeGenerator::get_eff_height(double x, double y, double z, double zenith, double azimuth) const {
    /*
        So this function finds the length of a chord passing through (x,y,z) at an angle (zenith, azimuth). 
        It gets the intersections with the cylinder, and then calculates the distance between those intersections

        Uses the same get-cylinder-intersection algorithm as LeptonInjector 
    */
    double r = vol_sim_details.Get_CylinderRadius();
    double cz1 = -1*vol_sim_details.Get_CylinderHeight()/2;
    double cz2 = -1*cz1;

    double nx = cos(azimuth)*sin(zenith);
    double ny = sin(azimuth)*sin(zenith);
    double nz = cos(zenith);

    double nx2 = nx*nx;
    double ny2 = ny*ny;
    double nr2 = nx2 + ny2;
    double n_sum = -(nx*x + ny*y);
    double r0_2 = x*x+y*y;
    
    if(nx==0.0 && ny==0.0){
        assert(nz!=0.0);
        return( vol_sim_details.Get_CylinderHeight() );
    }else{
        double root = sqrt(n_sum*n_sum - nr2*(r0_2-r*r));

        double sol_1 = (n_sum - root)/nr2;
        double sol_2 = (n_sum + root)/nr2;
        
        // positions corresponding to above solutions 
        double x1 = x + nx*sol_1;
        double y1 = y + ny*sol_1;
        double z1 = z + nz*sol_1;
        double x2 = x + nx*sol_2;
        double y2 = y + ny*sol_2;
        double z2 = z + nz*sol_2;

        // check if the solutions are within the z boundaries 
        bool b1_lower = z1<cz1;
        bool b2_lower = z2<cz1;
        bool b1_upper = z1>cz2;
        bool b2_upper = z2>cz2;
       
        bool bb_lower = b1_lower or b2_lower;
        bool bb_upper = b1_upper or b2_upper;
        bool bb = bb_lower or bb_upper;

        // these are the cyliner intersection points. Tentative solutions 
        double p1[] = {x1,y1,z1};
        double p2[] = {x2,y2,z2};
        // replace with encap intersections if necessary
        if (bb){
            double nr = sqrt(nr2);
            double r0 = sqrt(r0_2);
            if (bb_lower){
                double t1 = (cz1-z)/nz;
                double xx = x + nx*t1;
                double yy = y + ny*t1;
                double zz = cz1;
                if (b1_lower){
                    p1[0] = xx;
                    p1[1] = yy;
                    p1[2] = zz;
                }else{
                    p2[0] = xx;
                    p2[1] = yy;
                    p2[2] = zz;
                }
            }
            if (bb_upper){
                double t2 = (cz2-z)/nz;
                double xx = x + nx*t2;
                double yy = y + ny*t2;
                double zz = cz2;
                if (b1_upper){
                    p1[0] = xx;
                    p1[1] = yy;
                    p1[2] = zz;
                }else{
                    p2[0] = xx;
                    p2[1] = yy;
                    p2[2] = zz;
                }
                   
            }

        }// end if bb
    
    double dist_sq = pow(p2[0]-p1[0],2) + pow(p2[1]-p1[1],2) + pow(p2[2]-p1[2],2);
    return sqrt(dist_sq); 
    }//end big if

}//end function

double VolumeGenerator::probability_pos(double x, double y, double z, double zenith, double azimuth) const {
    if(abs(z)>vol_sim_details.Get_CylinderHeight()/2)
        return 0;

    double r = sqrt(x*x + y*y);
    if(r>vol_sim_details.Get_CylinderRadius())
        return 0;

    return get_eff_height(x,y,z,zenith,azimuth)/(1e4*M_PI*vol_sim_details.Get_CylinderRadius()*vol_sim_details.Get_CylinderRadius()*vol_sim_details.Get_CylinderHeight());
}

double RangeGenerator::number_of_targets(Event& e) const {
    return Constants::Na*e.total_column_depth;
}

double VolumeGenerator::number_of_targets(Event& e) const {
    return Constants::Na*e.total_column_depth;
}

// this method opens an hdf5 file with a name stored at "configuration_filename",
//  and returns a vector of Generator objects built from the information in that file! 
#define MAX_NAME 1024
std::vector<std::shared_ptr<Generator>> MakeGeneratorsFromH5File( std::string configuration_filename){
    // need to convert string to const char*
    const char * filename_ptr = configuration_filename.c_str();

    // load h5 file
    // open the file as read-only, no special flags
    hid_t file  = H5Fopen( filename_ptr , H5F_ACC_RDONLY, H5P_DEFAULT);
    // open up the base group
    hid_t group = H5Gopen2( file, "LIC_Base", H5P_DEFAULT); 
    
    //get the number of entries in the group (number of injectors)
    hsize_t nobj;
    herr_t error = H5Gget_num_objs( group, &nobj);
   
    ssize_t len;
    char member_name[MAX_NAME];
    std::vector<std::shared_ptr<Generator>> generator_vector;
    for (unsigned int config = 0; config < nobj; config++){
        // get entry name, assign it to /member_name/
        len                 = H5Gget_objname_by_idx( group, (hsize_t)config, member_name, (size_t)MAX_NAME);
        // use that entry name to open the dataset: this specific injector
        hid_t access_plist;
        hid_t dataset       = H5Dopen2( group, member_name, H5P_DEFAULT );
        // access the datatable 
        hsize_t datatable   = H5Topen2( group, member_name , H5T_COMPOUND );
        
        // get the name of the 12th and 13th members
        // use their identities to decide on RIC or VIC

        herr_t status;
        if (false){
            RangedInjectionConfiguration ric; 


            //fill in the Ranged Injection Configuration object 
            status = H5Tget_member_value( datatable, 0, &ric.number_of_events);
            status = H5Tget_member_value( datatable, 1, &ric.energyMin);
            status = H5Tget_member_value( datatable, 2, &ric.energyMax);
            status = H5Tget_member_value( datatable, 3, &ric.powerlawIndex);
            status = H5Tget_member_value( datatable, 4, &ric.azimuthMin);
            status = H5Tget_member_value( datatable, 5, &ric.azimuthMax);
            status = H5Tget_member_value( datatable, 6, &ric.zenithMin);
            status = H5Tget_member_value( datatable, 7, &ric.zenithMax);
            status = H5Tget_member_value( datatable, 8, &ric.final_state_particle_0);
            status = H5Tget_member_value( datatable, 9, &ric.final_state_particle_1);
            status = H5Tget_member_value( datatable,10, &ric.differentialCrossSectionData);
            status = H5Tget_member_value( datatable,11, &ric.totalCrossSectionData);
            status = H5Tget_member_value( datatable,12, &ric.injectionRadius);
            status = H5Tget_member_value( datatable,13, &ric.injectionCap);
            generator_vector.push_back(std::make_shared<RangeGenerator>(RangeSimulationDetails::MakeFromRangeInjectorConfiguration(ric)));
        }else{
            VolumeInjectionConfiguration vic; 
            //fill in the Ranged Injection Configuration object 
            status = H5Tget_member_value( datatable, 0, &vic.number_of_events);
            status = H5Tget_member_value( datatable, 1, &vic.energyMin);
            status = H5Tget_member_value( datatable, 2, &vic.energyMax);
            status = H5Tget_member_value( datatable, 3, &vic.powerlawIndex);
            status = H5Tget_member_value( datatable, 4, &vic.azimuthMin);
            status = H5Tget_member_value( datatable, 5, &vic.azimuthMax);
            status = H5Tget_member_value( datatable, 6, &vic.zenithMin);
            status = H5Tget_member_value( datatable, 7, &vic.zenithMax);
            status = H5Tget_member_value( datatable, 8, &vic.final_state_particle_0);
            status = H5Tget_member_value( datatable, 9, &vic.final_state_particle_1);
            status = H5Tget_member_value( datatable,10, &vic.differentialCrossSectionData);
            status = H5Tget_member_value( datatable,11, &vic.totalCrossSectionData);
            status = H5Tget_member_value( datatable,12, &vic.cylinderRadius);
            status = H5Tget_member_value( datatable,13, &vic.cylinderHeight);
            generator_vector.push_back(std::make_shared<VolumeGenerator>(VolumeSimulationDetails::MakeFromVolumeInjectorConfiguration(vic)));
        }

        // H5Tget_member_value( datatable, entry number, where to put the value );

    }
    // Flush all the memory accumulated by the hdf5 libraries 
    H5close();
    return generator_vector;
}

std::vector<std::shared_ptr<Generator>> MakeGeneratorsFromLICFile(std::string configuration_filename){
    std::ifstream is(configuration_filename,std::ios::binary);
    if(!is.good())
      throw std::runtime_error("LW::MakeGeneratorsFromLICFile: Configuration file " + configuration_filename + " does not exist or its corrupted.");
    is.seekg (0, is.end);
    int length = is.tellg();
    is.seekg (0, is.beg);
    std::vector<std::shared_ptr<Generator>> generator_vector;

    // read first header // expect particle enumerator definitions
    BlockHeader h;
    is >> h;
    if(h.block_name != "EnumDef")
        throw std::runtime_error("LW::MakeGeneratorsFromLICFile: Configuration file does not have a particle enumerator definitions. Got block " + h.block_name);
    if(not is.good() or is.eof())
        throw std::runtime_error("LW::MakeGeneratorsFromLICFile: Configuration file error while reading.");
    EnumDefBlock edb;
    is >> edb;

    // Trust
    //if(not CheckParticleEnumeration(edb))
    //    throw std::runtime_error("LW::MakeGeneratorsFromLICFile: Configuration file particle enumeration are not compatible with current definitions. Alarm.");

    while((not is.eof()) and is.good() and not (length==is.tellg())){
      // get all the simulations generators on the file
      if(not is.good() or is.eof())
          throw std::runtime_error("LW::MakeGeneratorsFromLICFile: Configuration file error while reading.");
      try {
        is >> h;
      } catch (std::runtime_error e){
        std::cout << e.what() << std::endl;
        break;
      }

      if(h.block_name == "RangedInjectionConfiguration"){
        RangedInjectionConfiguration ric;
        is >> ric;
        generator_vector.push_back(std::make_shared<RangeGenerator>(RangeSimulationDetails::MakeFromRangeInjectorConfiguration(ric)));

      } else if (h.block_name == "VolumeInjectionConfiguration"){
        VolumeInjectionConfiguration vic;
        is >> vic;
        generator_vector.push_back(std::make_shared<VolumeGenerator>(VolumeSimulationDetails::MakeFromVolumeInjectorConfiguration(vic)));
      } else {
        throw std::runtime_error("LW::MakeGeneratorsFromLICFile: Expected either VolumeSimulationDetails or RangedInjectionConfiguration block after enum definitions, but got " + h.block_name);
      }
    }

    is.close();
    return generator_vector;
}

/// print stuff
//std::ostream& operator<<(std::ostream& os, RangeSimulationDetails& e) {
//  return e.
//}
//std::ostream& operator<<(std::ostream& os, VolumeSimulationDetails& e);

} // namespace LW


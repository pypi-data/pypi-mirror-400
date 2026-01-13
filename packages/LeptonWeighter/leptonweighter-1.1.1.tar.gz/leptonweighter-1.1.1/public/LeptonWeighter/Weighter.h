#ifndef LW_WEIGHTER_H
#define LW_WEIGHTER_H

#include <vector>
#include <memory>
#include "MetaWeighter.h"
#include "Flux.h"
#include "CrossSection.h"
#include "Event.h"
#include "Generator.h"

#ifdef NUS_FOUND
#include <nuSQuIDS/taudecay.h>
#include <nuSQuIDS/AdaptiveQuad.h>
#endif

namespace LW {

///\class
///\brief Weighter class
class Weighter: public MetaWeighter<Weighter>{
    private:
        std::vector<std::shared_ptr<Flux>> fv;
        std::shared_ptr<CrossSection> cs;
        std::vector<std::shared_ptr<Generator>> gv;
    public:
        // cool constructors
        Weighter(
                std::vector<std::shared_ptr<Flux>> fv,
                std::shared_ptr<CrossSection> cs,
                std::vector<std::shared_ptr<Generator>> gv):
            fv(fv),cs(cs),gv(gv) {}

        Weighter(
                std::shared_ptr<Flux> flux,
                std::shared_ptr<CrossSection> cs,
                std::shared_ptr<Generator> g):
            Weighter(std::vector<std::shared_ptr<Flux>>{flux}, cs, std::vector<std::shared_ptr<Generator>>{g}){}

        Weighter(
                std::shared_ptr<Flux> flux,
                std::shared_ptr<CrossSection> cs,
                std::vector<std::shared_ptr<Generator>> gv):
            Weighter(std::vector<std::shared_ptr<Flux>>{flux},cs,gv){}

        Weighter(
                std::vector<std::shared_ptr<Flux>> fv,
                std::shared_ptr<CrossSection> cs,
                std::shared_ptr<Generator> g):
            Weighter(fv,cs,std::vector<std::shared_ptr<Generator>>{g}){}

        // uncool constructors assuming flux to be unit
        Weighter(std::shared_ptr<CrossSection> cs,std::vector<std::shared_ptr<Generator>> gv):Weighter(std::vector<std::shared_ptr<Flux>>{std::make_shared<ConstantFlux>(1)},cs,gv){}
        Weighter(std::shared_ptr<CrossSection> cs,std::shared_ptr<Generator> g):Weighter(std::vector<std::shared_ptr<Flux>>{std::make_shared<ConstantFlux>(1)},cs,std::vector<std::shared_ptr<Generator>>{g}){}
        // get stuff
        const std::vector<std::shared_ptr<Flux>> get_flux() const {
            return fv;
        }
        std::shared_ptr<const CrossSection> get_cross_section() const {
            return cs;
        }
        const std::vector<std::shared_ptr<Generator>> get_generators() const {
            return gv;
        }
        // set stuff
        void set_fluxes(std::vector<std::shared_ptr<Flux>> flux_in){
            if(flux_in.size() == 0)
                throw std::runtime_error("Weighter::set_fluxes: Vector array null length");
            fv = flux_in;
        }
        void add_flux(std::shared_ptr<Flux> f){
            fv.push_back(f);
        }
        void set_cross_section(std::shared_ptr<CrossSection> cs_in){
            cs = cs_in;
        }
        void add_generator(std::shared_ptr<Generator> g){
            gv.push_back(g);
        }
        void set_generators(std::vector<std::shared_ptr<Generator>> gv_in){
            if(gv_in.size() == 0)
                throw std::runtime_error("Weighter::set_generators: Vector array null length");
            gv=gv_in;
        }
        double get_total_flux(Event & e) const;
        // most important function of all
        double weight(Event & e) const;
        // most important function of all so you can call it in two ways
        double operator()(Event & e) const {return weight(e);}
        // compatibility mode
        double get_oneweight(Event & e) const;
#if defined(NUS_FOUND)
        // effective tau weight
        double get_effective_tau_oneweight(Event & e) const;
        double get_effective_tau_weight(Event & e) const;
#endif
};

} // namespace LW

#endif

#ifndef LW_NNFLUXINTERFACE_H_
#define LW_NNFLUXINTERFACE_H_

#include <memory>
#include <LeptonWeighter/Flux.h>
#include <LeptonWeighter/Utils.h>
#include <NewNuFlux/NewNuFlux.h>
#include <boost/shared_ptr.hpp>

namespace LW {
  //Stuff to enable converting between types of shared_ptrs
  namespace {
    template<class SharedPointer> struct Holder {
      SharedPointer p;

      Holder(const SharedPointer &p) : p(p) {}
      Holder(const Holder &other) : p(other.p) {}
      //Holder(Holder &&other) : p(std::move<SharedPointer>(other.p)) {}

      void operator () (...) const {}
      };

    template<class T> std::shared_ptr<T> to_std_ptr(const boost::shared_ptr<T> &p) {
      typedef Holder<std::shared_ptr<T>> H;
      if(H* h = boost::get_deleter<H, T>(p))
        return h->p;
      return std::shared_ptr<T>(p.get(), Holder<boost::shared_ptr<T>>(p));
    }

    template<class T> boost::shared_ptr<T> to_boost_ptr(const std::shared_ptr<T> &p){
      typedef Holder<boost::shared_ptr<T>> H;
      if(H* h = std::get_deleter<H, T>(p))
        return h->p;
      return boost::shared_ptr<T>(p.get(), Holder<std::shared_ptr<T>>(p));
    }
  } // close of unnamed namespace

  ///\class
  ///\brief class to interface NewNuFlux with LeptonWeighter
  class atmosNeutrinoFlux: public Flux {
  private:
    bool nugen_compatible;
    std::shared_ptr<NewNuFlux::FluxFunction> flux;
  public:
    virtual ~atmosNeutrinoFlux(){}
    atmosNeutrinoFlux(NewNuFlux::FluxFunction* f, bool nugen_compatible = false):flux(f),nugen_compatible(nugen_compatible){}
    atmosNeutrinoFlux(std::shared_ptr<NewNuFlux::FluxFunction> f, bool nugen_compatible = false):flux(f),nugen_compatible(nugen_compatible){}
    atmosNeutrinoFlux(boost::shared_ptr<NewNuFlux::FluxFunction> f, bool nugen_compatible = false):flux(to_std_ptr(f)),nugen_compatible(nugen_compatible){}
    double EvaluateFlux(const Event& e) const;
    double operator()(const Event& e) const{
      return EvaluateFlux(e);
    }
    std::shared_ptr<NewNuFlux::FluxFunction> get(){
      return(flux);
    }
  };
}// namespace LW

#endif

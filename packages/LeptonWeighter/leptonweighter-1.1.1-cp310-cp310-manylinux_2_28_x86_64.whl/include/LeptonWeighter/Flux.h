#ifndef LW_FLUX_H
#define LW_FLUX_H

#include <math.h>
#include <LeptonWeighter/MetaWeighter.h>
#include <LeptonWeighter/ParticleType.h>
#include <LeptonWeighter/Event.h>

/*
"Probablemente de todos nuestros sentimientos el único que no es verdaderamente
nuestro es la esperanza. La esperanza le pertenece a la vida, es la vida misma defendiéndose", Rayuela, Cortazar.
*/

namespace LW {

///\class
///\brief Abstract flux class
class Flux: public MetaWeighter<Flux> {
    public:
        using result_type=double;
        virtual result_type EvaluateFlux(const Event&) const = 0;
        result_type operator()(const Event& e) const { return EvaluateFlux(e);};
        virtual void EnableAveragedEval(double) {};
};

///\class
///\brief Constant trivial flux class
class ConstantFlux: public Flux {
    private:
        const double c;
    public:
        using result_type = double;
        result_type EvaluateFlux(const Event& e) const override {
            return c;
        };
        explicit ConstantFlux(double c): c(c) {};
};

///\class
///\brief PowerLawFlux trivial flux class
class PowerLawFlux: public Flux {
    private:
        const double normalization;
        const double spectral_index;
        const double pivot_point;
    public:
        using result_type = double;
        result_type EvaluateFlux(const Event& e) const override {
            return normalization*pow(e.energy/pivot_point,spectral_index);
        };
        explicit PowerLawFlux(double normalization, double spectral_index, double pivot_point=1e5): normalization(normalization), spectral_index(spectral_index), pivot_point(pivot_point) {};
};

} // namespace LW

#endif

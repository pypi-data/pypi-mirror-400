#ifndef LW_METAWEIGHTER_H
#define LW_METAWEIGHTER_H

namespace LW {

template<typename Derived>
class MetaWeighter {
    public:
        operator Derived &() {
            return (*static_cast<Derived *>(this));
        }

        operator const Derived&() const {
            return (*static_cast<Derived const *>(this));
        }
};

} // namespace LW

#endif

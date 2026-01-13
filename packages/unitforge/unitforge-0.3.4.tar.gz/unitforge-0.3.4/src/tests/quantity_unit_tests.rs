#![cfg(test)]
mod tests {
    use crate::*;
    use num_traits::Zero;

    #[test]
    fn test_new() {
        let input = 1000;
        let output = Distance::new(input.into(), DistanceUnit::mm);
        assert_eq!(
            output,
            Distance {
                multiplier: 1000f64,
                power: -3
            }
        )
    }

    #[test]
    fn optimize_on_add() {
        let f_1 = Force::new(10.0, ForceUnit::N);
        let f_2 = Force::new(1.0E12, ForceUnit::N);
        let f = f_1 + f_2;
        assert!(f.get_multiplier().log10().round() == 0.);
    }

    #[test]
    fn optimize_large() {
        let mut x = Force {
            multiplier: 1E10,
            power: 0,
        };
        x.optimize();
        assert!(x.get_multiplier().log10().round() == 0.);
        assert_eq!(x.to(ForceUnit::N), 1E10);
    }

    #[test]
    fn optimize_small() {
        let mut x = Force {
            multiplier: 1E-10,
            power: 0,
        };
        x.optimize();
        assert!(x.get_multiplier().log10().round() == 0.);
        assert_eq!(x.to(ForceUnit::N), 1E-10);
    }

    #[test]
    fn optimize_zero() {
        let mut f_1 = Force::zero();
        f_1.optimize();
        assert_eq!(f_1, Force::zero());
    }

    #[test]
    fn mul_with_self() {
        let a = Quantity::AreaQuantity(Area::new(10.0, AreaUnit::msq));
        let b = (a * a).unwrap();
        assert_eq!(
            b.to(Unit::AreaOfMomentUnit(AreaOfMomentUnit::mhc)).unwrap(),
            100.0
        );
    }

    #[test]
    fn sqrt() {
        let a = Quantity::AreaOfMomentQuantity(AreaOfMoment::new(25.0, AreaOfMomentUnit::mhc));
        let b = a.sqrt().unwrap();
        assert!((b.to(Unit::AreaUnit(AreaUnit::msq)).unwrap() - 5.0).abs() < 1E-10);
    }

    #[test]
    fn inverse_stress_from_stress_division() {
        let stress = Stress::new(2.0, StressUnit::Pa);
        let inverse = 1.0 / stress;
        assert!((inverse.to(InverseStressUnit::_Pa) - 0.5).abs() < 1E-12);
    }

    #[test]
    fn stress_from_inverse_stress_division() {
        let inverse = InverseStress::new(0.5, InverseStressUnit::_Pa);
        let stress = 1.0 / inverse;
        assert!((stress.to(StressUnit::Pa) - 2.0).abs() < 1E-12);
    }

    #[test]
    fn stress_squared_from_force_stress_over_area() {
        let force = Force::new(2.0, ForceUnit::N);
        let stress = Stress::new(3.0, StressUnit::Pa);
        let area = Area::new(6.0, AreaUnit::msq);
        let result = (force * stress) / area;
        assert!((result.to(StressSquaredUnit::Nsq_mmhc) - 1.0).abs() < 1E-12);
    }

    #[test]
    fn force_stress_from_stress_squared_times_area() {
        let stress_squared = StressSquared::new(2.0, StressSquaredUnit::Nsq_mmhc);
        let area = Area::new(3.0, AreaUnit::msq);
        let result = stress_squared * area;
        assert!((result.to(ForceStressUnit::Nsq_msq) - 6.0).abs() < 1E-12);
    }
}

import pytest
from unitforge import *


def test_inverse_stress_from_stress_division():
    stress = Stress(2.0, StressUnit.Pa)
    inverse = 1 / stress
    assert isinstance(inverse, InverseStress)
    assert inverse.to(InverseStressUnit._Pa) == pytest.approx(0.5)


def test_stress_from_inverse_stress_division():
    inverse = InverseStress(0.5, InverseStressUnit._Pa)
    stress = 1 / inverse
    assert isinstance(stress, Stress)
    assert stress.to(StressUnit.Pa) == pytest.approx(2.0)


def test_stress_squared_from_force_stress_over_area():
    force = Force(2.0, ForceUnit.N)
    stress = Stress(3.0, StressUnit.Pa)
    area = Area(6.0, AreaUnit.msq)
    result = (force * stress) / area
    assert isinstance(result, StressSquared)
    assert result.to(StressSquaredUnit.Nsq_mmhc) == pytest.approx(1.0)


def test_force_stress_from_stress_squared_times_area():
    stress_squared = StressSquared(2.0, StressSquaredUnit.Nsq_mmhc)
    area = Area(3.0, AreaUnit.msq)
    result = stress_squared * area
    assert isinstance(result, ForceStress)
    assert result.to(ForceStressUnit.Nsq_msq) == pytest.approx(6.0)

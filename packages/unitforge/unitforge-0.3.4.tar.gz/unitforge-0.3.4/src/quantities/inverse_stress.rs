use crate::impl_macros::macros::*;
use crate::prelude::*;
use crate::Stress;
use ndarray::{Array1, Array2, ArrayView1, ArrayView2};
use num_traits::identities::Zero;
use num_traits::FromPrimitive;
#[cfg(feature = "pyo3")]
use pyo3::pyclass;
#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};
use std::cmp::Ordering;
use std::fmt;
use std::ops::{Add, AddAssign, Div, DivAssign, Mul, MulAssign, Neg, Sub, SubAssign};
#[cfg(feature = "strum")]
use strum_macros::EnumIter;

#[cfg_attr(feature = "strum", derive(EnumIter))]
#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
#[derive(Copy, Clone, PartialEq, Debug)]
#[cfg_attr(feature = "pyo3", pyclass(eq, eq_int))]
pub enum InverseStressUnit {
    _Pa,
}

impl PhysicsUnit for InverseStressUnit {
    fn name(&self) -> &str {
        match &self {
            InverseStressUnit::_Pa => "1/Pa",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            InverseStressUnit::_Pa => (1., 0),
        }
    }
}

impl_quantity!(InverseStress, InverseStressUnit, [InverseStressUnit::_Pa]);
impl_div_with_self_to_f64!(InverseStress);
impl_mul!(InverseStress, Stress, f64);

impl Div<InverseStress> for f64 {
    type Output = Stress;

    fn div(self, rhs: InverseStress) -> Self::Output {
        Stress::from_raw(self / rhs.as_f64())
    }
}

#[cfg(feature = "pyo3")]
#[pymethods]
impl InverseStress {
    fn __rtruediv__(rhs: PyRef<Self>, lhs: f64) -> PyResult<Stress> {
        Ok(lhs / *rhs)
    }
}
